pub enum Nations {
    None,
    AustriaHungray,
    England, 
    France, 
    Germany,
    Italy,
    Russia,
    Turkey
}



struct Region {
    pub name: String,
    connected_regions : Vec<Region>,
    is_sea: bool,
    owner: Nations
}


impl Region {
    pub fn get_connected(&self) -> Vec<Region> {
        return self.connected_regions;
    }
}