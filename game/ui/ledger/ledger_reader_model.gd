class_name LedgerReaderModel
extends RefCounted
## The ledger's pages, Node-free (M5-A3P-1706; act3_ch17 B05). The scene writes entries (loc keys) on the open page
## and turns it; a turned page is gone and the next starts blank. Nothing is ever written after the ledger's last
## entry, so the pages after it stay blank (the blank-page end). The view is LedgerReader.

## Each page's entries, in order; the last is the open page.
var pages: Array[PackedStringArray] = [PackedStringArray()]


## Writes the entry `key` on the open page.
func write(key: String) -> void:
	pages[-1].append(key)


## Turns the open page: the next comes up blank.
func turn() -> void:
	pages.append(PackedStringArray())


## The open page's entries (empty: a blank page).
func current() -> PackedStringArray:
	return pages[-1]


## How many pages have been turned.
func turned() -> int:
	return pages.size() - 1


## The blank pages at the end, the open one included (0 while it has an entry, and before the first entry).
func blank_turns() -> int:
	var n := 0
	for i in range(pages.size() - 1, -1, -1):
		if not pages[i].is_empty():
			return n
		n += 1
	return 0
