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

import json

import logging
logger = logging.getLogger(__name__)

import requests

import traceback

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
            logger.info("Event.type = %s,event.state_key=%s,event.room_id=%s",event.type,event.state_key,event.room_id)
            room_id = "!amPfLyNnQCdeGbFgMm:matrix.local" #event.room_id
            requester = create_requester('@admin:'+self.server_name, "syt_YWRtaW4_LQSDuXTmsrLjeegTeohm_3MPJch")
            admin = UserID.from_string('@admin:'+self.server_name)
            admin_requester = create_requester(
                admin, authenticated_entity=requester.authenticated_entity
            )
            event_dict = event.get_dict()
            logger.info(event_dict)
            new_event_content = await self._api.http_client.post_json_get_json(
                uri="https://demo.expo.local/test", post_json=event_dict,
            )
            try:
                # https://github.com/matrix-org/synapse/blob/develop/synapse/handlers/room_summary.py#L257
                room_summary_handler =self._homeserver.get_room_summary_handler()
                logger.info("Request hierarchy for room_id =%s",room_id)
                rooms = await room_summary_handler.get_room_hierarchy(
                    admin_requester,
                    room_id,
                    suggested_only=False,
                    max_depth=1,
                    limit=None,
                )
                #wenn keine rooms da, dann falsche Zugriff oder es gibt keine, sollte aber nicht möglich sein!
                if 'rooms' not in rooms:
                    logger.info('NO ROOMS')
                    return None

                for room in rooms['rooms'] :
                    if 'room_type' in room and room['room_type'] == 'm.space':
                        continue

                    logger.info("RoomiD = %s, roomName = %s",room['room_id'],room['name'])

                    # Make the user join the room.
                    #await self._api.update_room_membership(
                    #    sender=event.state_key,
                    #    target=event.state_key,
                    #    room_id=event.room_id,
                    #    new_membership="invite",
                    #)
            except Exception as e:
                logger.info(traceback.format_exc())
                return None;


