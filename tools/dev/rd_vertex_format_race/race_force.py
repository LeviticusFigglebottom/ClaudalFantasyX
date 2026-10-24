# M1-QA-10: force the Godot 4.6.3 RenderingDevice vertex-format race under gdb (run by run.sh).
# 1. The race.gd worker thread stops in render_pipeline_create() just after `vertex_formats.has()`
#    passed (rendering_device.cpp:4166), i.e. after it released the RD lock.
# 2. Only the main thread runs, until vertex_format_create() is inside the vertex_formats
#    HashMap::_resize_and_rehash and has reset `_size` to 0 (old elements not yet re-inserted).
# 3. Only the worker runs: its non-const operator[] misses, default-inserts an EMPTY
#    VertexDescriptionCache, and validation fails with the gate's message (location 0).
# 4. Everything runs on; RD shutdown then frees that entry's null driver_id (SIGSEGV).
# A fixed engine (locked getptr, as in 4.7) never reaches step 3's error line.
import os

import gdb

DBG = os.environ["QA10_DBG_DIR"]


def ex(c):
    print(">>> " + c)
    gdb.execute(c)


ex("set pagination off")
ex("set auto-load safe-path /")
ex("set confirm off")
ex("set print thread-events off")
ex("handle SIGPIPE nostop noprint pass")
ex("set breakpoint pending on")
ex("symbol-file %s/godot.debug" % DBG)
# only the race.gd worker passes the out-of-range primitive 1000
ex("break rendering_device.cpp:4166 if (int)p_render_primitive == 1000")
ex("run")
worker = gdb.selected_thread()
print("QA10 worker thread", worker.num, "stopped after has() in render_pipeline_create")
ex("bt 2")
ex("disable 1")
ex("set scheduler-locking on")
ex("thread 1")
ex(
    "break HashMap<long, RenderingDevice::VertexDescriptionCache, HashMapHasherDefault, "
    "HashMapComparatorDefault<long, void>, DefaultTypedAllocator<HashMapElement<long, "
    "RenderingDevice::VertexDescriptionCache> > >::_resize_and_rehash"
)
ex("continue")
print("QA10 main thread entered vertex_formats _resize_and_rehash")
ex("p this->_size")
addr = int(gdb.parse_and_eval("(unsigned long)&this->_size"))
ex("delete 2")
ex("watch -l *(unsigned int *)%d" % addr)
ex("continue")
print("QA10 main thread inside vertex_formats rehash: _size reset, old elements not yet re-inserted")
ex("p *(unsigned int *)%d" % addr)
ex("delete")
ex("break rendering_device.cpp:4182")
ex("thread %d" % worker.num)
ex("continue")
print("QA10 worker reached the 'vertex input location not provided' error line")
ex("p i")
ex("p vd.vertex_formats._cowdata._ptr")
ex("set scheduler-locking off")
ex("delete")
ex("continue")
