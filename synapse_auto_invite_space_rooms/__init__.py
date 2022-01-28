from typing import Any, Dict

from synapse.module_api import EventBase, ModuleApi

from synapse.types import (
    create_requester,
    UserID,
    UserInfo,
    JsonDict,
    RoomAlias,
    RoomID,
)

from synapse.http.servlet import (
    ResolveRoomIdMixin,
    RestServlet,
    assert_params_in_dict,
    parse_boolean,
    parse_integer,
    parse_json_object_from_request,
    parse_string,
    parse_strings_from_args,
)

import requests

class InviteSpaceRooms:
    def __init__(self, config: Dict[str, Any], api: ModuleApi):
        # Keep a reference to the Module API.
        self._api = api
        self._homeserver = api._hs 
        self._room_member_handler = self._homeserver.get_room_member_handler()
        self.server_name  = self._homeserver.config.server.server_name


        # Register the callback.
        self._api.register_third_party_rules_callbacks(
            on_new_event=self.on_invite_event,
        )

    async def on_invite_event(self, event: EventBase, *args: Any) -> None:
        """Listens for new events, and if the event is an invite for a local user then
        automatically accepts it.

        Args:
            event: The incoming event.
        """
        # Check if the event is an invite for a local user.
        if (
            event.type == "m.room.member"
            and event.is_state()
            and event.membership == "invite"
            and self._api.is_mine(event.state_key)
        ):
            #
            room_id = event.room_id
            requester = create_requester('@admin:'+self.server_name, "syt_YWRtaW4_LQSDuXTmsrLjeegTeohm_3MPJch")
            admin = UserID.from_string('@admin:'+self.server_name)
            admin_requester = create_requester(
                admin, authenticated_entity=requester.authenticated_entity
            )


            rooms = await self._room_member_handler._room_summary_handler.get_room_hierarchy(
                requester,
                room_id,
                suggested_only=False,
                max_depth=None,
                limit=None,
                from_token=parse_string(request, "from"),
            )

            # Make the user join the room.
            await self._api.update_room_membership(
                sender=event.state_key,
                target=event.state_key,
                room_id=event.room_id,
                new_membership="invite",
            )
