import json
from typing import TextIO

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World
from .Coordinates import generate_random_coordinates
from .DBLayout import generate_random_db_layout
from .Items import OuterWildsItem, all_non_event_items_table, item_name_groups, create_item, create_items
from .LocationsAndRegions import all_non_event_locations_table, location_name_groups, create_regions
from .Options import OuterWildsGameOptions


class OuterWildsWebWorld(WebWorld):
    theme = "dirt"
    tutorials = [
        Tutorial(
            tutorial_name="Setup Guide",
            description="A guide to playing Outer Wilds.",
            language="English",
            file_name="guide_en.md",
            link="guide/en",
            authors=["Ixrec"]
        )
    ]


class OuterWildsWorld(World):
    game = "Outer Wilds"
    web = OuterWildsWebWorld()

    eotu_coordinates = 'vanilla'
    db_layout = 'vanilla'

    def generate_early(self) -> None:
        self.eotu_coordinates = generate_random_coordinates(self.random) \
            if self.options.randomize_coordinates else "vanilla"
        self.db_layout = generate_random_db_layout(self.random) \
            if self.options.randomize_dark_bramble_layout else "vanilla"

    # members and methods implemented by LocationsAndRegions.py, locations.jsonc and connections.jsonc

    location_name_to_id = all_non_event_locations_table
    location_name_groups = location_name_groups

    def create_regions(self) -> None:
        create_regions(self)

    # members and methods implemented by Items.py and items.jsonc

    item_name_to_id = all_non_event_items_table
    item_name_groups = item_name_groups

    def create_item(self, name: str) -> OuterWildsItem:
        return create_item(self.player, name)

    def create_items(self) -> None:
        create_items(self)

    def get_filler_item_name(self) -> str:
        # Used in corner cases (e.g. plando, item_links, start_inventory_from_pool)
        # where even a well-behaved world may end up "missing" items.
        # Technically this "should" be a random choice among all filler/trap items
        # the world is configured to have, but it's not worth that much effort.
        return "Marshmallow"

    # members and methods related to Options.py

    options_dataclass = OuterWildsGameOptions
    options: OuterWildsGameOptions

    # miscellaneous smaller methods

    def set_rules(self) -> None:
        # here we only set the completion condition; all the location/region rules were set in create_regions()
        option_key_to_item_name = {
            'song_of_five': "Victory - Song of Five",
            'song_of_six': "Victory - Song of Six",
        }

        goal_item = option_key_to_item_name[self.options.goal.current_key]
        self.multiworld.completion_condition[self.player] = lambda state: state.has(goal_item, self.player)

    def fill_slot_data(self):
        slot_data = self.options.as_dict("goal", "death_link", "logsanity")
        slot_data["eotu_coordinates"] = self.eotu_coordinates
        slot_data["db_layout"] = self.db_layout
        # Archipelago does not yet have apworld versions (data_version is deprecated),
        # so we have to roll our own with slot_data for the time being
        slot_data["apworld_version"] = "0.2.0"
        return slot_data

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        if self.eotu_coordinates != 'vanilla':
            spoiler_handle.write('\nRandomized Eye of the Universe Coordinates'
                                 '\n0-5 are the points of the hexagon, starting at '
                                 'the rightmost point and going counterclockwise'
                                 '\n\n%s\n%s\n%s\n\n' % (json.dumps(self.eotu_coordinates[0]),
                                                         json.dumps(self.eotu_coordinates[1]),
                                                         json.dumps(self.eotu_coordinates[2])))
        if self.db_layout != 'vanilla':
            spoiler_handle.write('\nRandomized Dark Bramble Layout'
                                 '\nRoom names are (H)ub, (E)scapePod, (A)nglerNest, '
                                 '(P)ioneer, E(X)itOnly, (V)essel, (C)luster, (S)mallNest'
                                 '\n\n%s\n\n' % self.db_layout.replace('|', '\n'))
