class_name BattlePortraits
extends RefCounted
## The picture a battle HUD slot shows for a fighter (Act I final pass, ADR 0041): a hero's face crop
## (HeroPortraits, the "battle" page's emotion, "fallen" while down) or an enemy's bestiary portrait
## (CreaturePortraits). Null for anyone without one (a Vowbound, a fighter whose model is not built
## yet): the slot then keeps its initial. A combatant id's base is the part before "#".


static func texture(cid: StringName, fallen: bool = false) -> Texture2D:
	var base := StringName(String(cid).get_slice("#", 0))
	var face := HeroPortraits.face(base, HeroPortraits.page_emotion(&"battle", fallen))
	if face != null:
		return face
	return CreaturePortraits.texture(base)
