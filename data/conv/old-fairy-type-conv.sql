create table old_fairy_type_pokemon_working (
  pokemon_id TEXT,
  pokemon_identifier TEXT,
  type_name TEXT,
  slot TEXT,
  primary key (pokemon_id, type_name)
);
.mode csv
.import old-fairy-types.csv old_fairy_type_pokemon_working
create table pokemon_types_hx (
  pokemon_id TEXT,
  type_id TEXT,
  slot TEXT,
  before_generation_id TEXT,
  primary key (pokemon_id, type_id)
);
insert into pokemon_types_hx
(pokemon_id, type_id, slot, before_generation_id)
select oft.pokemon_id, t.id, oft.slot, 6
from old_fairy_type_pokemon_working oft
join types t on t.identifier = oft.type_name;
