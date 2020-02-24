.headers on
select * from (
  select
    z.*
  , (z.attack + z.special_attack) total_attack
  , (z.defense + z.special_defense) total_defense
  , (z.hp + z.defense + z.special_defense) total_hp_and_defense
  , (z.attack + z.speed) attack_and_speed
  , (z.special_attack + z.speed) special_attack_and_speed
  , (z.best_attack + z.speed) best_attack_and_speed
  from (
    select
      p.identifier
    , min(cast(vg.generation_id as int)) generation
    , max(case when s.identifier = 'hp' then cast(ps.base_stat as int) else 0 end) hp
    , max(case when s.identifier = 'attack' then cast(ps.base_stat as int) else 0 end) attack
    , max(case when s.identifier = 'defense' then cast(ps.base_stat as int) else 0 end) defense
    , max(case when s.identifier = 'special-attack' then cast(ps.base_stat as int) else 0 end) special_attack
    , max(case when s.identifier = 'special-defense' then cast(ps.base_stat as int) else 0 end) special_defense
    , max(case when s.identifier = 'speed' then cast(ps.base_stat as int) else 0 end) speed
    , max(case when s.identifier in ('attack', 'special-attack') then cast(ps.base_stat as int) else 0 end) best_attack
    from pokemon p
    join pokemon_dex_numbers pdn on pdn.species_id = p.species_id
    join pokedex_version_groups pvg on pvg.pokedex_id = pdn.pokedex_id
    join version_groups vg on vg.id = pvg.version_group_id
    join pokedexes dex on dex.id = pvg.pokedex_id
    join pokemon_stats ps on ps.pokemon_id = p.id
    join stats s on s.id = ps.stat_id
    where 1=1
      and p.is_default = '1'
      and cast(vg.generation_id as int) <= 5
      and dex.is_main_series = '1'
    group by p.identifier
  ) z
) z
where speed >= 90
order by best_attack desc
