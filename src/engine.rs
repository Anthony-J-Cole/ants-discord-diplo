

// Move, hold, support, convoy
// Move/attack
pub enum Actions {
    Hold, // default
    Move,
    Support,
    Convoy // only for fleets 
}




// Armies bounce on the same turn they try to move onto the same space
// Bounce = stay put (in most scenarios)

// Support needs to check if sup target is adjacent.
// when *resolving* is when sup targets move is adjacent should be checked.

// each region should have a unit ID associated 

// order of resolving
// 1. Holds apply 1 defensive strength to region
// 2. Support Holds (if targeting a valid region) add 1 defensvie strength to that region.
// 3. Temp: Convoys
// 4. Move to unocupied (resolves)
// 5. Attack occupied
//      Calculate all support attacks and apply offensive strength to region
// 6. Resolve attacks loss?
// 7. Resolve attacks win? 

// TODO: bounce logic
