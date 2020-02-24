-- Top Pokemon by stat
select distinct p.identifier, ps.base_stat
from pokemon p
join pokemon_dex_numbers pdn on pdn.species_id = p.species_id
join pokemon_stats ps on ps.pokemon_id = p.id
join stats s on s.id = ps.stat_id
where s.identifier = 'special-defense'
  and p.is_default = '1'
  and pdn.pokedex_id in (
    select pvg.pokedex_id
    from pokedex_version_groups pvg
    join pokedexes dex on dex.id = pvg.pokedex_id
    where cast(pvg.version_group_id as int) <= 5
      and dex.is_main_series = '1'
  )
order by cast(ps.base_stat as int) desc
