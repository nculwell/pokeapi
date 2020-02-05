CREATE TABLE abilities(
  "id" TEXT,
  "identifier" TEXT,
  "generation_id" TEXT,
  "is_main_series" TEXT
  , primary key (id)
);
CREATE TABLE ability_changelog(
  "id" TEXT,
  "ability_id" TEXT,
  "changed_in_version_group_id" TEXT
  , primary key (id, ability_id)
);
CREATE TABLE ability_names(
  "ability_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (ability_id, local_language_id)
);
CREATE TABLE berries(
  "id" TEXT,
  "item_id" TEXT,
  "firmness_id" TEXT,
  "natural_gift_power" TEXT,
  "natural_gift_type_id" TEXT,
  "size" TEXT,
  "max_harvest" TEXT,
  "growth_time" TEXT,
  "soil_dryness" TEXT,
  "smoothness" TEXT
  , primary key (id)
);
CREATE TABLE berry_firmness(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE berry_firmness_names(
  "berry_firmness_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (berry_firmness_id, local_language_id)
);
CREATE TABLE berry_flavors(
  "berry_id" TEXT,
  "contest_type_id" TEXT,
  "flavor" TEXT
  , primary key (berry_id, contest_type_id)
);
CREATE TABLE characteristic_text(
  "characteristic_id" TEXT,
  "local_language_id" TEXT,
  "message" TEXT
  , primary key (characteristic_id, local_language_id)
);
CREATE TABLE characteristics(
  "id" TEXT,
  "stat_id" TEXT,
  "gene_mod_5" TEXT
  , primary key (id)
);
CREATE TABLE contest_combos(
  "first_move_id" TEXT,
  "second_move_id" TEXT
  , primary key ("first_move_id", second_move_id)
);
CREATE TABLE contest_effects(
  "id" TEXT,
  "appeal" TEXT,
  "jam" TEXT
  , primary key (id)
);
CREATE TABLE contest_type_names(
  "contest_type_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT,
  "flavor" TEXT,
  "color" TEXT
  , primary key (contest_type_id, local_language_id)
);
CREATE TABLE contest_types(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE egg_groups(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE encounter_condition_value_map(
  "encounter_id" TEXT,
  "encounter_condition_value_id" TEXT
  , primary key (encounter_id, encounter_condition_value_id)
);
CREATE TABLE encounter_condition_values(
  "id" TEXT,
  "encounter_condition_id" TEXT,
  "identifier" TEXT,
  "is_default" TEXT
  , primary key (id)
);
CREATE TABLE encounter_conditions(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE encounter_methods(
  "id" TEXT,
  "identifier" TEXT,
  "order" TEXT
  , primary key (id)
);
CREATE TABLE encounter_slots(
  "id" TEXT,
  "version_group_id" TEXT,
  "encounter_method_id" TEXT,
  "slot" TEXT,
  "rarity" TEXT
  , primary key (id)
);
CREATE TABLE encounters(
  "id" TEXT,
  "version_id" TEXT,
  "location_area_id" TEXT,
  "encounter_slot_id" TEXT,
  "pokemon_id" TEXT,
  "min_level" TEXT,
  "max_level" TEXT
  , primary key (id)
);
CREATE TABLE evolution_chains(
  "id" TEXT,
  "baby_trigger_item_id" TEXT
  , primary key (id)
);
CREATE TABLE evolution_triggers(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE experience(
  "growth_rate_id" TEXT,
  "level" TEXT,
  "experience" TEXT
  , primary key (growth_rate_id, "level")
);
CREATE TABLE genders(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE generation_names(
  "generation_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (generation_id, local_language_id)
);
CREATE TABLE generations(
  "id" TEXT,
  "main_region_id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE growth_rates(
  "id" TEXT,
  "identifier" TEXT,
  "formula" TEXT
  , primary key (id)
);
CREATE TABLE item_categories(
  "id" TEXT,
  "pocket_id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE item_flag_map(
  "item_id" TEXT,
  "item_flag_id" TEXT
  , primary key (item_id, item_flag_id)
);
CREATE TABLE item_flags(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE item_fling_effects(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE item_game_indices(
  "item_id" TEXT,
  "generation_id" TEXT,
  "game_index" TEXT
  , primary key (item_id, generation_id)
);
CREATE TABLE item_names(
  "item_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (item_id, local_language_id)
);
CREATE TABLE item_pocket_names(
  "item_pocket_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (item_pocket_id, local_language_id)
);
CREATE TABLE item_pockets(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE items(
  "id" TEXT,
  "identifier" TEXT,
  "category_id" TEXT,
  "cost" TEXT,
  "fling_power" TEXT,
  "fling_effect_id" TEXT
  , primary key (id)
);
CREATE TABLE language_names(
  "language_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (language_id, local_language_id)
);
CREATE TABLE languages(
  "id" TEXT,
  "iso639" TEXT,
  "iso3166" TEXT,
  "identifier" TEXT,
  "official" TEXT,
  "order" TEXT
  , primary key (id)
);
CREATE TABLE location_area_encounter_rates(
  "location_area_id" TEXT,
  "encounter_method_id" TEXT,
  "version_id" TEXT,
  "rate" TEXT
  , primary key (location_area_id, encounter_method_id, version_id)
);
CREATE TABLE location_areas(
  "id" TEXT,
  "location_id" TEXT,
  "game_index" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE location_game_indices(
  "location_id" TEXT,
  "generation_id" TEXT,
  "game_index" TEXT
  , primary key (location_id, generation_id, game_index)
);
CREATE TABLE location_names(
  "location_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT,
  "subtitle" TEXT
  , primary key (location_id, local_language_id)
);
CREATE TABLE locations(
  "id" TEXT,
  "region_id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE machines(
  "machine_number" TEXT,
  "version_group_id" TEXT,
  "item_id" TEXT,
  "move_id" TEXT
  , primary key (machine_number, version_group_id)
);
CREATE TABLE move_battle_styles(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE move_changelog(
  "move_id" TEXT,
  "changed_in_version_group_id" TEXT,
  "type_id" TEXT,
  "power" TEXT,
  "pp" TEXT,
  "accuracy" TEXT,
  "priority" TEXT,
  "target_id" TEXT,
  "effect_id" TEXT,
  "effect_chance" TEXT
  , primary key (move_id, changed_in_version_group_id)
);
CREATE TABLE move_damage_classes(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE move_effect_changelog(
  "id" TEXT,
  "effect_id" TEXT,
  "changed_in_version_group_id" TEXT
  , primary key (id)
);
CREATE TABLE move_effects(
  "id" TEXT
  , primary key (id)
);
CREATE TABLE move_flag_map(
  "move_id" TEXT,
  "move_flag_id" TEXT
  , primary key (move_id, move_flag_id)
);
CREATE TABLE move_flags(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE move_meta(
  "move_id" TEXT,
  "meta_category_id" TEXT,
  "meta_ailment_id" TEXT,
  "min_hits" TEXT,
  "max_hits" TEXT,
  "min_turns" TEXT,
  "max_turns" TEXT,
  "drain" TEXT,
  "healing" TEXT,
  "crit_rate" TEXT,
  "ailment_chance" TEXT,
  "flinch_chance" TEXT,
  "stat_chance" TEXT
  , primary key (move_id)
);
CREATE TABLE move_meta_ailment_names(
  "move_meta_ailment_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (move_meta_ailment_id, local_language_id)
);
CREATE TABLE move_meta_ailments(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE move_meta_categories(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE move_meta_stat_changes(
  "move_id" TEXT,
  "stat_id" TEXT,
  "change" TEXT
  , primary key (move_id, stat_id)
);
CREATE TABLE move_names(
  "move_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (move_id, local_language_id)
);
CREATE TABLE move_targets(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE moves(
  "id" TEXT,
  "identifier" TEXT,
  "generation_id" TEXT,
  "type_id" TEXT,
  "power" TEXT,
  "pp" TEXT,
  "accuracy" TEXT,
  "priority" TEXT,
  "target_id" TEXT,
  "damage_class_id" TEXT,
  "effect_id" TEXT,
  "effect_chance" TEXT,
  "contest_type_id" TEXT,
  "contest_effect_id" TEXT,
  "super_contest_effect_id" TEXT
  , primary key (id)
);
CREATE TABLE nature_battle_style_preferences(
  "nature_id" TEXT,
  "move_battle_style_id" TEXT,
  "low_hp_preference" TEXT,
  "high_hp_preference" TEXT
  , primary key (nature_id, move_battle_style_id)
);
CREATE TABLE nature_names(
  "nature_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (nature_id, local_language_id)
);
CREATE TABLE nature_pokeathlon_stats(
  "nature_id" TEXT,
  "pokeathlon_stat_id" TEXT,
  "max_change" TEXT
  , primary key (nature_id, pokeathlon_stat_id)
);
CREATE TABLE natures(
  "id" TEXT,
  "identifier" TEXT,
  "decreased_stat_id" TEXT,
  "increased_stat_id" TEXT,
  "hates_flavor_id" TEXT,
  "likes_flavor_id" TEXT,
  "game_index" TEXT
  , primary key (id)
);
CREATE TABLE pal_park(
  "species_id" TEXT,
  "area_id" TEXT,
  "base_score" TEXT,
  "rate" TEXT
  , primary key (species_id, area_id)
);
CREATE TABLE pal_park_area_names(
  "pal_park_area_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (pal_park_area_id, local_language_id)
);
CREATE TABLE pal_park_areas(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokeathlon_stat_names(
  "pokeathlon_stat_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (pokeathlon_stat_id, local_language_id)
);
CREATE TABLE pokeathlon_stats(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokedex_version_groups(
  "pokedex_id" TEXT,
  "version_group_id" TEXT
  , primary key (pokedex_id, version_group_id)
);
CREATE TABLE pokedexes(
  "id" TEXT,
  "region_id" TEXT,
  "identifier" TEXT,
  "is_main_series" TEXT
  , primary key (id)
);
CREATE TABLE pokemon(
  "id" TEXT,
  "identifier" TEXT,
  "species_id" TEXT,
  "height" TEXT,
  "weight" TEXT,
  "base_experience" TEXT,
  "order" TEXT,
  "is_default" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_abilities(
  "pokemon_id" TEXT,
  "ability_id" TEXT,
  "is_hidden" TEXT,
  "slot" TEXT
  , primary key (pokemon_id, ability_id)
);
CREATE TABLE pokemon_color_names(
  "pokemon_color_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (pokemon_color_id, local_language_id)
);
CREATE TABLE pokemon_colors(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_dex_numbers(
  "species_id" TEXT,
  "pokedex_id" TEXT,
  "pokedex_number" TEXT
  , primary key (species_id, pokedex_id)
);
CREATE TABLE pokemon_egg_groups(
  "species_id" TEXT,
  "egg_group_id" TEXT
  , primary key (species_id, egg_group_id)
);
CREATE TABLE pokemon_evolution(
  "id" TEXT,
  "evolved_species_id" TEXT,
  "evolution_trigger_id" TEXT,
  "trigger_item_id" TEXT,
  "minimum_level" TEXT,
  "gender_id" TEXT,
  "location_id" TEXT,
  "held_item_id" TEXT,
  "time_of_day" TEXT,
  "known_move_id" TEXT,
  "known_move_type_id" TEXT,
  "minimum_happiness" TEXT,
  "minimum_beauty" TEXT,
  "minimum_affection" TEXT,
  "relative_physical_stats" TEXT,
  "party_species_id" TEXT,
  "party_type_id" TEXT,
  "trade_species_id" TEXT,
  "needs_overworld_rain" TEXT,
  "turn_upside_down" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_form_generations(
  "pokemon_form_id" TEXT,
  "generation_id" TEXT,
  "game_index" TEXT
  , primary key (pokemon_form_id, generation_id)
);
CREATE TABLE pokemon_form_names(
  "pokemon_form_id" TEXT,
  "local_language_id" TEXT,
  "form_name" TEXT,
  "pokemon_name" TEXT
  , primary key (pokemon_form_id, local_language_id)
);
CREATE TABLE pokemon_form_pokeathlon_stats(
  "pokemon_form_id" TEXT,
  "pokeathlon_stat_id" TEXT,
  "minimum_stat" TEXT,
  "base_stat" TEXT,
  "maximum_stat" TEXT
  , primary key (pokemon_form_id, pokeathlon_stat_id)
);
CREATE TABLE pokemon_forms(
  "id" TEXT,
  "identifier" TEXT,
  "form_identifier" TEXT,
  "pokemon_id" TEXT,
  "introduced_in_version_group_id" TEXT,
  "is_default" TEXT,
  "is_battle_only" TEXT,
  "is_mega" TEXT,
  "form_order" TEXT,
  "order" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_game_indices(
  "pokemon_id" TEXT,
  "version_id" TEXT,
  "game_index" TEXT
  , primary key (pokemon_id, version_id)
);
CREATE TABLE pokemon_habitat_names(
  "pokemon_habitat_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (pokemon_habitat_id, local_language_id)
);
CREATE TABLE pokemon_habitats(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_items(
  "pokemon_id" TEXT,
  "version_id" TEXT,
  "item_id" TEXT,
  "rarity" TEXT
  , primary key (pokemon_id, version_id, item_id)
);
CREATE TABLE pokemon_move_methods(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_moves(
  "pokemon_id" TEXT,
  "version_group_id" TEXT,
  "move_id" TEXT,
  "pokemon_move_method_id" TEXT,
  "level" TEXT,
  "order" TEXT
  , primary key (pokemon_id, version_group_id, move_id, pokemon_move_method_id, "level")
);
CREATE TABLE pokemon_shapes(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_species(
  "id" TEXT,
  "identifier" TEXT,
  "generation_id" TEXT,
  "evolves_from_species_id" TEXT,
  "evolution_chain_id" TEXT,
  "color_id" TEXT,
  "shape_id" TEXT,
  "habitat_id" TEXT,
  "gender_rate" TEXT,
  "capture_rate" TEXT,
  "base_happiness" TEXT,
  "is_baby" TEXT,
  "hatch_counter" TEXT,
  "has_gender_differences" TEXT,
  "growth_rate_id" TEXT,
  "forms_switchable" TEXT,
  "order" TEXT,
  "conquest_order" TEXT
  , primary key (id)
);
CREATE TABLE pokemon_species_names(
  "pokemon_species_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT,
  "genus" TEXT
  , primary key (pokemon_species_id, local_language_id)
);
CREATE TABLE pokemon_stats(
  "pokemon_id" TEXT,
  "stat_id" TEXT,
  "base_stat" TEXT,
  "effort" TEXT
  , primary key (pokemon_id, stat_id)
);
CREATE TABLE pokemon_types(
  "pokemon_id" TEXT,
  "type_id" TEXT,
  "slot" TEXT
  , primary key (pokemon_id, type_id, slot)
);
CREATE TABLE region_names(
  "region_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (region_id, local_language_id)
);
CREATE TABLE regions(
  "id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
CREATE TABLE stat_names(
  "stat_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (stat_id, local_language_id)
);
CREATE TABLE stats(
  "id" TEXT,
  "damage_class_id" TEXT,
  "identifier" TEXT,
  "is_battle_only" TEXT,
  "game_index" TEXT
  , primary key (id)
);
CREATE TABLE super_contest_combos(
  "first_move_id" TEXT,
  "second_move_id" TEXT
  , primary key (first_move_id, second_move_id)
);
CREATE TABLE super_contest_effects(
  "id" TEXT,
  "appeal" TEXT
  , primary key (id)
);
CREATE TABLE type_efficacy(
  "damage_type_id" TEXT,
  "target_type_id" TEXT,
  "damage_factor" TEXT
  , primary key (damage_type_id, target_type_id)
);
CREATE TABLE type_game_indices(
  "type_id" TEXT,
  "generation_id" TEXT,
  "game_index" TEXT
  , primary key (type_id, generation_id)
);
CREATE TABLE type_names(
  "type_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (type_id, local_language_id)
);
CREATE TABLE types(
  "id" TEXT,
  "identifier" TEXT,
  "generation_id" TEXT,
  "damage_class_id" TEXT
  , primary key (id)
);
CREATE TABLE version_group_pokemon_move_methods(
  "version_group_id" TEXT,
  "pokemon_move_method_id" TEXT
  , primary key (version_group_id, pokemon_move_method_id)
);
CREATE TABLE version_group_regions(
  "version_group_id" TEXT,
  "region_id" TEXT
  , primary key (version_group_id, region_id)
);
CREATE TABLE version_groups(
  "id" TEXT,
  "identifier" TEXT,
  "generation_id" TEXT,
  "order" TEXT
  , primary key (id)
);
CREATE TABLE version_names(
  "version_id" TEXT,
  "local_language_id" TEXT,
  "name" TEXT
  , primary key (version_id, local_language_id)
);
CREATE TABLE versions(
  "id" TEXT,
  "version_group_id" TEXT,
  "identifier" TEXT
  , primary key (id)
);
