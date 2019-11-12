#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# apt-get install python3-dev python3-pip -y
# python3 -m pip install colorama twilio readchar requests

from time import sleep
from threading import Thread
from colorama import init
from twilio.rest import Client
from requests_toolbelt import MultipartEncoder

import atexit, requests, hashlib, random
import readchar, hmac, uuid, os, string
import requests
import random
import json
import hashlib
import hmac
import urllib
import uuid
import time
import copy
import math
import sys
import os
#Turn off InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


BREAK = 3
LINE_FEED = 13
BACK_SPACE = 127 if os.name == "posix" else 8

ERROR = "[\x1b[31m-\x1b[39m]"
SUCCESS = "[\x1b[32m+\x1b[39m]"
INPUT = "[\x1b[33m?\x1b[39m]"
INFO = "[\x1b[35m*\x1b[39m]"

IG_ACCNT_LOGOUT = "{{\"phone_id\":\"{}\",\"guid\":\"{}\",\"device_id\":\"{}\"}}"
IG_EDIT_PROFILE = "{{\"gender\":\"3\",\"username\":\"{}\",\"first_name\":\"Reckless\",\"biography\":\"Welcome home!\",\"email\":\"{}\"}}"
IG_LOGIN_ACTUAL = "{{\"phone_id\":\"{}\",\"username\":\"{}\",\"adid\":\"{}\",\"guid\":\"{}\",\"device_id\":\"{}\",\"password\":\"{}\",\"login_attempt_count\":\"0\"}}"

IG_API_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
IG_API_USER_AGENT = "Instagram 84.0.0.21.105 Android (24/7.0; 380dpi; 1080x1920; OnePlus; ONEPLUS A3010; OnePlus3T; qcom; en_US; 145652094)"

class Signatures(object):
	def __init__(self):
		super(Signatures, self).__init__()
		self.key = b"02271fcedc24c5849a7505120650925e2b4c5b041e0a0bb0f82f4d41cfcdc944"

	def gen_uuid(self):
		return str(uuid.uuid4())

	def gen_device_id(self):
		return "android-{}".format(hashlib.md5(self.gen_uuid().encode("utf-8")).hexdigest()[:16])

	def gen_signature(self, data):
		return hmac.new(self.key, str.encode(data), hashlib.sha256).hexdigest()

	def sign_post_data(self, data):
		return "signed_body={}.{}&ig_sig_key_version=4".format(self.gen_signature(data), data)

class Device(object):
	def __init__(self):
		super(Device, self).__init__()
		self.filepath = os.path.expanduser("~/.madara-turbo.ini")

		if (os.path.isfile(self.filepath)):
			if (self.read_ini(self.filepath)):
				return

		self.create_device_ini()
		self.write_ini(self.filepath)

	def create_device_ini(self):
		self.adid = Signatures().gen_uuid()
		self.uuid = Signatures().gen_uuid()
		self.phone_id = Signatures().gen_uuid()
		self.device_id = Signatures().gen_device_id()

	def read_ini(self, filename):
		lines = [line.rstrip("\r\n") for line in open(filename, "r")]

		for line in lines:
			if (line.startswith("adid=")):
				self.adid = line.split("=")[1]
			elif (line.startswith("uuid=")):
				self.uuid = line.split("=")[1]
			elif (line.startswith("phoneid=")):
				self.phone_id = line.split("=")[1]
			elif (line.startswith("deviceid=")):
				self.device_id = line.split("=")[1]

		return None not in (self.adid, self.uuid, self.phone_id, self.device_id)

	def write_ini(self, filename):
		print("; Madara's Instagram Turbo", file=open(filename, "w"))
		print("; Information used for device identification\r\n", file=open(filename, "a"))
		print("[Device]\r\nadid={}\r\nuuid={}".format(self.adid, self.uuid), file=open(filename, "a"))
		print("phoneid={}\r\ndeviceid={}".format(self.phone_id, self.device_id), file=open(filename, "a"))

class InstagramAPI:
    API_URL = 'https://i.instagram.com/api/v1/'
    DEVICE_SETTINTS = {'manufacturer': 'Xiaomi',
                       'model': 'HM 1SW',
                       'android_version': 18,
                       'android_release': '4.3'}
    USER_AGENT = 'Instagram 10.26.0 Android ({android_version}/{android_release}; 320dpi; 720x1280; {manufacturer}; {model}; armani; qcom; en_US)'.format(**DEVICE_SETTINTS)
    IG_SIG_KEY = '4e99365f601b738512ad80361e528e420485645d61b41d1287f11c8dbcae5503'
    EXPERIMENTS = 'ig_promote_reach_objective_fix_universe,ig_android_universe_video_production,ig_search_client_h1_2017_holdout,ig_android_live_follow_from_comments_universe,ig_android_carousel_non_square_creation,ig_android_live_analytics,ig_android_follow_all_dialog_confirmation_copy,ig_android_stories_server_coverframe,ig_android_video_captions_universe,ig_android_offline_location_feed,ig_android_direct_inbox_retry_seen_state,ig_android_ontact_invite_universe,ig_android_live_broadcast_blacklist,ig_android_insta_video_reconnect_viewers,ig_android_ad_async_ads_universe,ig_android_search_clear_layout_universe,ig_android_shopping_reporting,ig_android_stories_surface_universe,ig_android_verified_comments_universe,ig_android_preload_media_ahead_in_current_reel,android_instagram_prefetch_suggestions_universe,ig_android_reel_viewer_fetch_missing_reels_universe,ig_android_direct_search_share_sheet_universe,ig_android_business_promote_tooltip,ig_android_direct_blue_tab,ig_android_async_network_tweak_universe,ig_android_elevate_main_thread_priority_universe,ig_android_stories_gallery_nux,ig_android_instavideo_remove_nux_comments,ig_video_copyright_whitelist,ig_react_native_inline_insights_with_relay,ig_android_direct_thread_message_animation,ig_android_draw_rainbow_client_universe,ig_android_direct_link_style,ig_android_live_heart_enhancements_universe,ig_android_rtc_reshare,ig_android_preload_item_count_in_reel_viewer_buffer,ig_android_users_bootstrap_service,ig_android_auto_retry_post_mode,ig_android_shopping,ig_android_main_feed_seen_state_dont_send_info_on_tail_load,ig_fbns_preload_default,ig_android_gesture_dismiss_reel_viewer,ig_android_tool_tip,ig_android_ad_logger_funnel_logging_universe,ig_android_gallery_grid_column_count_universe,ig_android_business_new_ads_payment_universe,ig_android_direct_links,ig_android_audience_control,ig_android_live_encore_consumption_settings_universe,ig_perf_android_holdout,ig_android_cache_contact_import_list,ig_android_links_receivers,ig_android_ad_impression_backtest,ig_android_list_redesign,ig_android_stories_separate_overlay_creation,ig_android_stop_video_recording_fix_universe,ig_android_render_video_segmentation,ig_android_live_encore_reel_chaining_universe,ig_android_sync_on_background_enhanced_10_25,ig_android_immersive_viewer,ig_android_mqtt_skywalker,ig_fbns_push,ig_android_ad_watchmore_overlay_universe,ig_android_react_native_universe,ig_android_profile_tabs_redesign_universe,ig_android_live_consumption_abr,ig_android_story_viewer_social_context,ig_android_hide_post_in_feed,ig_android_video_loopcount_int,ig_android_enable_main_feed_reel_tray_preloading,ig_android_camera_upsell_dialog,ig_android_ad_watchbrowse_universe,ig_android_internal_research_settings,ig_android_search_people_tag_universe,ig_android_react_native_ota,ig_android_enable_concurrent_request,ig_android_react_native_stories_grid_view,ig_android_business_stories_inline_insights,ig_android_log_mediacodec_info,ig_android_direct_expiring_media_loading_errors,ig_video_use_sve_universe,ig_android_cold_start_feed_request,ig_android_enable_zero_rating,ig_android_reverse_audio,ig_android_branded_content_three_line_ui_universe,ig_android_live_encore_production_universe,ig_stories_music_sticker,ig_android_stories_teach_gallery_location,ig_android_http_stack_experiment_2017,ig_android_stories_device_tilt,ig_android_pending_request_search_bar,ig_android_fb_topsearch_sgp_fork_request,ig_android_seen_state_with_view_info,ig_android_animation_perf_reporter_timeout,ig_android_new_block_flow,ig_android_story_tray_title_play_all_v2,ig_android_direct_address_links,ig_android_stories_archive_universe,ig_android_save_collections_cover_photo,ig_android_live_webrtc_livewith_production,ig_android_sign_video_url,ig_android_stories_video_prefetch_kb,ig_android_stories_create_flow_favorites_tooltip,ig_android_live_stop_broadcast_on_404,ig_android_live_viewer_invite_universe,ig_android_promotion_feedback_channel,ig_android_render_iframe_interval,ig_android_accessibility_logging_universe,ig_android_camera_shortcut_universe,ig_android_use_one_cookie_store_per_user_override,ig_profile_holdout_2017_universe,ig_android_stories_server_brushes,ig_android_ad_media_url_logging_universe,ig_android_shopping_tag_nux_text_universe,ig_android_comments_single_reply_universe,ig_android_stories_video_loading_spinner_improvements,ig_android_collections_cache,ig_android_comment_api_spam_universe,ig_android_facebook_twitter_profile_photos,ig_android_shopping_tag_creation_universe,ig_story_camera_reverse_video_experiment,ig_android_direct_bump_selected_recipients,ig_android_ad_cta_haptic_feedback_universe,ig_android_vertical_share_sheet_experiment,ig_android_family_bridge_share,ig_android_search,ig_android_insta_video_consumption_titles,ig_android_stories_gallery_preview_button,ig_android_fb_auth_education,ig_android_camera_universe,ig_android_me_only_universe,ig_android_instavideo_audio_only_mode,ig_android_user_profile_chaining_icon,ig_android_live_video_reactions_consumption_universe,ig_android_stories_hashtag_text,ig_android_post_live_badge_universe,ig_android_swipe_fragment_container,ig_android_search_users_universe,ig_android_live_save_to_camera_roll_universe,ig_creation_growth_holdout,ig_android_sticker_region_tracking,ig_android_unified_inbox,ig_android_live_new_watch_time,ig_android_offline_main_feed_10_11,ig_import_biz_contact_to_page,ig_android_live_encore_consumption_universe,ig_android_experimental_filters,ig_android_search_client_matching_2,ig_android_react_native_inline_insights_v2,ig_android_business_conversion_value_prop_v2,ig_android_redirect_to_low_latency_universe,ig_android_ad_show_new_awr_universe,ig_family_bridges_holdout_universe,ig_android_background_explore_fetch,ig_android_following_follower_social_context,ig_android_video_keep_screen_on,ig_android_ad_leadgen_relay_modern,ig_android_profile_photo_as_media,ig_android_insta_video_consumption_infra,ig_android_ad_watchlead_universe,ig_android_direct_prefetch_direct_story_json,ig_android_shopping_react_native,ig_android_top_live_profile_pics_universe,ig_android_direct_phone_number_links,ig_android_stories_weblink_creation,ig_android_direct_search_new_thread_universe,ig_android_histogram_reporter,ig_android_direct_on_profile_universe,ig_android_network_cancellation,ig_android_background_reel_fetch,ig_android_react_native_insights,ig_android_insta_video_audio_encoder,ig_android_family_bridge_bookmarks,ig_android_data_usage_network_layer,ig_android_universal_instagram_deep_links,ig_android_dash_for_vod_universe,ig_android_modular_tab_discover_people_redesign,ig_android_mas_sticker_upsell_dialog_universe,ig_android_ad_add_per_event_counter_to_logging_event,ig_android_sticky_header_top_chrome_optimization,ig_android_rtl,ig_android_biz_conversion_page_pre_select,ig_android_promote_from_profile_button,ig_android_live_broadcaster_invite_universe,ig_android_share_spinner,ig_android_text_action,ig_android_own_reel_title_universe,ig_promotions_unit_in_insights_landing_page,ig_android_business_settings_header_univ,ig_android_save_longpress_tooltip,ig_android_constrain_image_size_universe,ig_android_business_new_graphql_endpoint_universe,ig_ranking_following,ig_android_stories_profile_camera_entry_point,ig_android_universe_reel_video_production,ig_android_power_metrics,ig_android_sfplt,ig_android_offline_hashtag_feed,ig_android_live_skin_smooth,ig_android_direct_inbox_search,ig_android_stories_posting_offline_ui,ig_android_sidecar_video_upload_universe,ig_android_promotion_manager_entry_point_universe,ig_android_direct_reply_audience_upgrade,ig_android_swipe_navigation_x_angle_universe,ig_android_offline_mode_holdout,ig_android_live_send_user_location,ig_android_direct_fetch_before_push_notif,ig_android_non_square_first,ig_android_insta_video_drawing,ig_android_swipeablefilters_universe,ig_android_live_notification_control_universe,ig_android_analytics_logger_running_background_universe,ig_android_save_all,ig_android_reel_viewer_data_buffer_size,ig_direct_quality_holdout_universe,ig_android_family_bridge_discover,ig_android_react_native_restart_after_error_universe,ig_android_startup_manager,ig_story_tray_peek_content_universe,ig_android_profile,ig_android_high_res_upload_2,ig_android_http_service_same_thread,ig_android_scroll_to_dismiss_keyboard,ig_android_remove_followers_universe,ig_android_skip_video_render,ig_android_story_timestamps,ig_android_live_viewer_comment_prompt_universe,ig_profile_holdout_universe,ig_android_react_native_insights_grid_view,ig_stories_selfie_sticker,ig_android_stories_reply_composer_redesign,ig_android_streamline_page_creation,ig_explore_netego,ig_android_ig4b_connect_fb_button_universe,ig_android_feed_util_rect_optimization,ig_android_rendering_controls,ig_android_os_version_blocking,ig_android_encoder_width_safe_multiple_16,ig_search_new_bootstrap_holdout_universe,ig_android_snippets_profile_nux,ig_android_e2e_optimization_universe,ig_android_comments_logging_universe,ig_shopping_insights,ig_android_save_collections,ig_android_live_see_fewer_videos_like_this_universe,ig_android_show_new_contact_import_dialog,ig_android_live_view_profile_from_comments_universe,ig_fbns_blocked,ig_formats_and_feedbacks_holdout_universe,ig_android_reduce_view_pager_buffer,ig_android_instavideo_periodic_notif,ig_search_user_auto_complete_cache_sync_ttl,ig_android_marauder_update_frequency,ig_android_suggest_password_reset_on_oneclick_login,ig_android_promotion_entry_from_ads_manager_universe,ig_android_live_special_codec_size_list,ig_android_enable_share_to_messenger,ig_android_background_main_feed_fetch,ig_android_live_video_reactions_creation_universe,ig_android_channels_home,ig_android_sidecar_gallery_universe,ig_android_upload_reliability_universe,ig_migrate_mediav2_universe,ig_android_insta_video_broadcaster_infra_perf,ig_android_business_conversion_social_context,android_ig_fbns_kill_switch,ig_android_live_webrtc_livewith_consumption,ig_android_destroy_swipe_fragment,ig_android_react_native_universe_kill_switch,ig_android_stories_book_universe,ig_android_all_videoplayback_persisting_sound,ig_android_draw_eraser_universe,ig_direct_search_new_bootstrap_holdout_universe,ig_android_cache_layer_bytes_threshold,ig_android_search_hash_tag_and_username_universe,ig_android_business_promotion,ig_android_direct_search_recipients_controller_universe,ig_android_ad_show_full_name_universe,ig_android_anrwatchdog,ig_android_qp_kill_switch,ig_android_2fac,ig_direct_bypass_group_size_limit_universe,ig_android_promote_simplified_flow,ig_android_share_to_whatsapp,ig_android_hide_bottom_nav_bar_on_discover_people,ig_fbns_dump_ids,ig_android_hands_free_before_reverse,ig_android_skywalker_live_event_start_end,ig_android_live_join_comment_ui_change,ig_android_direct_search_story_recipients_universe,ig_android_direct_full_size_gallery_upload,ig_android_ad_browser_gesture_control,ig_channel_server_experiments,ig_android_video_cover_frame_from_original_as_fallback,ig_android_ad_watchinstall_universe,ig_android_ad_viewability_logging_universe,ig_android_new_optic,ig_android_direct_visual_replies,ig_android_stories_search_reel_mentions_universe,ig_android_threaded_comments_universe,ig_android_mark_reel_seen_on_Swipe_forward,ig_internal_ui_for_lazy_loaded_modules_experiment,ig_fbns_shared,ig_android_capture_slowmo_mode,ig_android_live_viewers_list_search_bar,ig_android_video_single_surface,ig_android_offline_reel_feed,ig_android_video_download_logging,ig_android_last_edits,ig_android_exoplayer_4142,ig_android_post_live_viewer_count_privacy_universe,ig_android_activity_feed_click_state,ig_android_snippets_haptic_feedback,ig_android_gl_drawing_marks_after_undo_backing,ig_android_mark_seen_state_on_viewed_impression,ig_android_live_backgrounded_reminder_universe,ig_android_live_hide_viewer_nux_universe,ig_android_live_monotonic_pts,ig_android_search_top_search_surface_universe,ig_android_user_detail_endpoint,ig_android_location_media_count_exp_ig,ig_android_comment_tweaks_universe,ig_android_ad_watchmore_entry_point_universe,ig_android_top_live_notification_universe,ig_android_add_to_last_post,ig_save_insights,ig_android_live_enhanced_end_screen_universe,ig_android_ad_add_counter_to_logging_event,ig_android_blue_token_conversion_universe,ig_android_exoplayer_settings,ig_android_progressive_jpeg,ig_android_offline_story_stickers,ig_android_gqls_typing_indicator,ig_android_chaining_button_tooltip,ig_android_video_prefetch_for_connectivity_type,ig_android_use_exo_cache_for_progressive,ig_android_samsung_app_badging,ig_android_ad_holdout_watchandmore_universe,ig_android_offline_commenting,ig_direct_stories_recipient_picker_button,ig_insights_feedback_channel_universe,ig_android_insta_video_abr_resize,ig_android_insta_video_sound_always_on'''
    SIG_KEY_VERSION = '4'

    # username            # Instagram username
    # password            # Instagram password
    # debug               # Debug
    # uuid                # UUID
    # device_id           # Device ID
    # username_id         # Username ID
    # token               # _csrftoken
    # isLoggedIn          # Session status
    # rank_token          # Rank token
    # IGDataPath          # Data storage path

    def __init__(self, username, password, debug=False, IGDataPath=None):
        m = hashlib.md5()
        
        m.update(username.encode('utf-8') + password.encode('utf-8'))
        self.device_id = self.generateDeviceId(m.hexdigest())
        self.setUser(username, password)

        self.isLoggedIn = False
        self.LastResponse = None
        self.s = requests.Session()

    def setUser(self, username, password):
        self.username = username
        self.password = password
        self.uuid = self.generateUUID(True)

    def setProxy(self, proxy=None):
        """
        Set proxy for all requests::

        Proxy format - user:password@ip:port
        """
        

        if proxy is not None:
            print('Set proxy!')
            proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
            self.s.proxies.update(proxies)

    def login(self, force=False):
        if (not self.isLoggedIn or force):
            if (self.SendRequest('si/fetch_headers/?challenge_type=signup&guid=' + self.generateUUID(False), None, True)):
                

                data = {'phone_id': self.generateUUID(True),
                        '_csrftoken': self.LastResponse.cookies['csrftoken'],
                        'username': self.username,
                        'guid': self.uuid,
                        'device_id': self.device_id,
                        'password': self.password,
                        'login_attempt_count': '0'}

                if (self.SendRequest('accounts/login/', self.generateSignature(json.dumps(data)), True)):
                    self.isLoggedIn = True
                    self.username_id = self.LastJson["logged_in_user"]["pk"]
                    self.rank_token = "%s_%s" % (self.username_id, self.uuid)
                    self.token = self.LastResponse.cookies["csrftoken"]

                    print("Login success!\n")
                    return True

    def syncFeatures(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           'id': self.username_id,
                           '_csrftoken': self.token,
                           'experiments': self.EXPERIMENTS})
        return self.SendRequest('qe/sync/', self.generateSignature(data))

    def logout(self):
        logout = self.SendRequest('accounts/logout/')

    def direct_message(self, text, recipients):
            if type(recipients) != type([]):
                recipients = [str(recipients)]
            recipient_users = '"",""'.join(str(r) for r in recipients)
            endpoint = 'direct_v2/threads/broadcast/text/'
            boundary = self.uuid
            bodies   = [
                {
                    'type' : 'form-data',
                    'name' : 'recipient_users',
                    'data' : '[["{}"]]'.format(recipient_users),
                },
                {
                    'type' : 'form-data',
                    'name' : 'client_context',
                    'data' : self.uuid,
                },
                {
                    'type' : 'form-data',
                    'name' : 'thread',
                    'data' : '["0"]',
                },
                {
                    'type' : 'form-data',
                    'name' : 'text',
                    'data' : text or '',
                },
            ]
            data = self.buildBody(bodies,boundary)
            self.s.headers.update (
                {
                    'User-Agent' : self.USER_AGENT,
                    'Proxy-Connection' : 'keep-alive',
                    'Connection': 'keep-alive',
                    'Accept': '*/*',
                    'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
                    'Accept-Language': 'en-en',
                }
            )
            #self.SendRequest(endpoint,post=data) #overwrites 'Content-type' header and boundary is missed
            response = self.s.post(self.API_URL + endpoint, data=data)
            
            if response.status_code == 200:
                self.LastResponse = response
                self.LastJson = json.loads(response.text)
                return True
            else:
                print ("Request return " + str(response.status_code) + " error!")
                # for debugging
                try:
                    self.LastResponse = response
                    self.LastJson = json.loads(response.text)
                except:
                    pass
                return False
        

    def changePassword(self, newPassword):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token,
                           'old_password': self.password,
                           'new_password1': newPassword,
                           'new_password2': newPassword})
        return self.SendRequest('accounts/change_password/', self.generateSignature(data))

    def setPrivateAccount(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token})
        return self.SendRequest('accounts/set_private/', self.generateSignature(data))

    def setPublicAccount(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token})
        return self.SendRequest('accounts/set_public/', self.generateSignature(data))

    def getProfileData(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token})
        return self.SendRequest('accounts/current_user/?edit=true', self.generateSignature(data))

    def editProfile(self, url, phone, first_name, biography, email, gender):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token,
                           'external_url': url,
                           'phone_number': phone,
                           'username': self.username,
                           'full_name': first_name,
                           'biography': biography,
                           'email': email,
                           'gender': gender})
        return self.SendRequest('accounts/edit_profile/', self.generateSignature(data))

    def getUsernameInfo(self, usernameId):
        return self.SendRequest('users/' + str(usernameId) + '/info/')

    def getSelfUsernameInfo(self):
        return self.getUsernameInfo(self.username_id)

    def getSelfSavedMedia(self):
        return self.SendRequest('feed/saved')

    def getRecentActivity(self):
        activity = self.SendRequest('news/inbox/?')
        return activity

    def getFollowingRecentActivity(self):
        activity = self.SendRequest('news/?')
        return activity

    def getv2Inbox(self):
        inbox = self.SendRequest('direct_v2/inbox/?')
        return inbox

    def getv2Threads(self, thread, cursor=None):
        endpoint = 'direct_v2/threads/{0}'.format(thread)
        if cursor is not None:
            endpoint += '?cursor={0}'.format(cursor)
        inbox = self.SendRequest(endpoint)
        return inbox

    def getUserTags(self, usernameId):
        tags = self.SendRequest('usertags/' + str(usernameId) + '/feed/?rank_token=' + str(self.rank_token) + '&ranked_content=true&')
        return tags

    def getSelfUserTags(self):
        return self.getUserTags(self.username_id)

    def tagFeed(self, tag):
        userFeed = self.SendRequest('feed/tag/' + str(tag) + '/?rank_token=' + str(self.rank_token) + '&ranked_content=true&')
        return userFeed

    def getMediaLikers(self, mediaId):
        likers = self.SendRequest('media/' + str(mediaId) + '/likers/?')
        return likers

    def getGeoMedia(self, usernameId):
        locations = self.SendRequest('maps/user/' + str(usernameId) + '/')
        return locations

    def getSelfGeoMedia(self):
        return self.getGeoMedia(self.username_id)

    def fbUserSearch(self, query):
        query = self.SendRequest('fbsearch/topsearch/?context=blended&query=' + str(query) + '&rank_token=' + str(self.rank_token))
        return query

    def searchUsers(self, query):
        query = self.SendRequest('users/search/?ig_sig_key_version=' + str(self.SIG_KEY_VERSION) + '&is_typeahead=true&query=' + str(query) + '&rank_token=' + str(self.rank_token))
        return query

    def searchUsername(self, usernameName):
        query = self.SendRequest('users/' + str(usernameName) + '/usernameinfo/')

    def getLikedMedia(self, maxid=''):
        return self.SendRequest('feed/liked/?max_id=' + str(maxid))

    def generateSignature(self, data, skip_quote=False):
        if not skip_quote:
            try:
                parsedData = urllib.parse.quote(data)
            except AttributeError:
                parsedData = urllib.quote(data)
        else:
            parsedData = data
        return 'ig_sig_key_version=' + self.SIG_KEY_VERSION + '&signed_body=' + hmac.new(self.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() + '.' + parsedData

    def generateDeviceId(self, seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def generateUUID(self, type):
        generated_uuid = str(uuid.uuid4())
        if (type):
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    def generateUploadId(self):
        return str(calendar.timegm(datetime.utcnow().utctimetuple()))

    def buildBody(self, bodies, boundary):
        body = u''
        for b in bodies:
            body += u'--{boundary}\r\n'.format(boundary=boundary)
            body += u'Content-Disposition: {b_type}; name="{b_name}"'.format(b_type=b['type'], b_name=b['name'])
            _filename = b.get('filename', None)
            _headers = b.get('headers', None)
            if _filename:
                _filename, ext = os.path.splitext(_filename)
                _body += u'; filename="pending_media_{uid}.{ext}"'.format(uid=self.generateUploadId(), ext=ext)
            if _headers and isinstance(_headers, list):
                for h in _headers:
                    _body += u'\r\n{header}'.format(header=h)
            body += u'\r\n\r\n{data}\r\n'.format(data=b['data'])
        body += u'--{boundary}--'.format(boundary=boundary)
        return body

    def SendRequest(self, endpoint, post=None, login=False):
        verify = False  # don't show request warning

        if (not self.isLoggedIn and not login):
            raise Exception("Not logged in!\n")

        self.s.headers.update({'Connection': 'close',
                               'Accept': '*/*',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'User-Agent': self.USER_AGENT})

        while True:
            try:
                if (post is not None):
                    response = self.s.post(self.API_URL + endpoint, data=post, verify=verify)
                else:
                    response = self.s.get(self.API_URL + endpoint, verify=verify)
                break
            except Exception as e:
                print('Except on SendRequest (wait 60 sec and resend): ' + str(e))
                time.sleep(60)

        if response.status_code == 200:
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            return True
        else:
            #print("Request return " + str(response.status_code) + " error!")
            # for debugging
            try:
                self.LastResponse = response
                self.LastJson = json.loads(response.text)
                #print(self.LastJson)
            except:
                pass
            return False

    def dm(self, message, username):
        """
        USAGE:
        Make sure class object is already made
        param message: message to send
        param username: username to send to
        """
        self.login()
        self.searchUsername(username) #example 'cassianokunsch'
        response = self.LastJson
        user_id = response['user']['pk']
        paste = message
        self.direct_message(paste, [user_id])
        if (self.LastJson['status']) == 'ok':
            print('DM sent')
        

class Instagram(object):
	def __init__(self):
		super(Instagram, self).__init__()
		self.device = Device()
		self.url = "https://i.instagram.com/api/v1"

		self.rs = 0
		self.attempts = 0
		self.running = True
		self.logged_in = False
		self.session_id = None
		self.csrf_token = None

		self.email = None
		self.username = None
		self.spam_blocked = False
		self.rate_limited = False
		self.missed_swap = False
		self.claimed = False

	def login(self, username, password):
		response = requests.post(self.url + "/accounts/login/", headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"Content-Type": IG_API_CONTENT_TYPE,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, data=Signatures().sign_post_data(IG_LOGIN_ACTUAL.format(
			self.device.phone_id, username, self.device.adid, self.device.uuid, self.device.device_id, password
		)))

		if (response.status_code == 200):
			self.session_id = response.cookies["sessionid"]
			self.csrf_token = response.cookies["csrftoken"]

		response = response.json()

		if (response["status"] == "fail"):
			if (response["message"] == "challenge_required"):
				print("{} Please verify this login and make sure 2FA is disabled".format(ERROR))
			else:
				print("{} {}".format(ERROR, response["message"]))
		elif (response["status"] == "ok"):
			self.logged_in = True

			if (self.get_profile_info()):
				print("{} Successfully logged in".format(SUCCESS))
				return self.logged_in
			else:
				print("{} Successfully logged in but failed to fetch profile information, this may be due to a rate limit".format(ERROR))
		else:
			print("{} An unknown login error occured".format(ERROR))

		return False

	def logout(self):
		if (not self.logged_in):
			return False

		return "\"status\": \"ok\"" in requests.post(self.url + "/accounts/logout/", headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"Content-Type": IG_API_CONTENT_TYPE,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, data=Signatures().sign_post_data(IG_ACCNT_LOGOUT.format(
			self.device.phone_id, self.device.uuid, self.device.device_id
		)), cookies={
			"sessionid": self.session_id
		}).text

	def update_consent(self):
		response = requests.post(self.url + "/consent/update_dob/", headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"Content-Type": IG_API_CONTENT_TYPE,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, data=Signatures().sign_post_data(
			"{\"current_screen_key\":\"dob\",\"day\":\"1\",\"year\":\"1998\",\"month\":\"1\"}"
		), cookies={
			"sessionid": self.session_id
		})

		if ("\"status\": \"ok\"" in response.text):
			print("{} Successfully updated consent to GDPR".format(SUCCESS))
			return self.get_profile_info()

		print("{} Failed to consent to GDPR, use an IP that is not from Europe".format(ERROR))
		return False

	def get_profile_info(self):
		response = requests.get(self.url + "/accounts/current_user/?edit=true", headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, cookies={
			"sessionid": self.session_id
		})

		if ("\"consent_required\"" in response.text):
			return self.update_consent()
		elif ("few minutes" in response.text):
			return False

		response = response.json()
		self.email = response["user"]["email"]
		self.username = response["user"]["username"]

		return self.email is not None and self.username is not None

	def build_claim_data(self):
		self.check_url = "{}/feed/user/{}/username/".format(self.url, self.target)
		self.claim_data = Signatures().sign_post_data(IG_EDIT_PROFILE.format(self.target, self.email))

	def target_available(self):
		response = requests.get(self.check_url, headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, cookies={
			"sessionid": self.session_id,
			"ds_user_id": random_id(random.choice([9, 10, 11, 12]))
		}, timeout=1)

		if ("few minutes" in response.text):
			self.rate_limited = True

		return len(response.text) == 47

	def claim_target(self):
		response = requests.post(self.url + "/accounts/edit_profile/", headers={
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-US",
			"User-Agent": IG_API_USER_AGENT,
			"Content-Type": IG_API_CONTENT_TYPE,
			"X-IG-Capabilities": "3brTvw==",
			"X-IG-Connection-Type": "WIFI"
		}, cookies={
			"sessionid": self.session_id
		}, data=self.claim_data)

		if ("feedback_required" in response.text):
			self.spam_blocked = True

		return "\"status\": \"ok\"" in response.text

class Turbo(Thread):
	def __init__(self, instagram):
		super(Turbo, self).__init__()
		self.instagram = instagram

	def run(self):
		while (self.instagram.running):
			try:
				if (self.instagram.target_available()):
					if (self.instagram.claim_target()):
						self.instagram.claimed = True
					else:
						self.instagram.missed_swap = True

					self.instagram.running = False

				if (self.instagram.spam_blocked or self.instagram.rate_limited):
					self.instagram.running = False

				self.instagram.attempts += 1
				sleep(0.18)
			except:
				continue

class RequestsPS(Thread):
	def __init__(self, instagram):
		super(RequestsPS, self).__init__()
		self.instagram = instagram

	def run(self):
		while self.instagram.running:
			before = self.instagram.attempts
			sleep(1) # Sleep 1 second, calc difference
			self.instagram.rs = self.instagram.attempts - before

def random_id(length):
	return "".join(random.choice(string.digits) for _ in range(length))

def get_input(prompt, mask=False):
	ret_str = b""
	print(prompt, end="", flush=True)

	while (True):
		ch = readchar.readchar()

		if (os.name == "posix"):
			ch = str.encode(ch)

		code_point = ord(ch)

		if (code_point == BREAK): # Ctrl-C
			if (os.name == "posix"):
				print("\r\n", end="", flush=True)

			exit(0)
		elif (code_point == LINE_FEED): # Linefeed
			break
		elif (code_point == BACK_SPACE): # Backspace
			if (len(ret_str) > 0):
				ret_str = ret_str[:-1]
				print("\b \b", end="", flush=True)
		else:
			ret_str += ch
			print("*" if mask else ch.decode("utf-8"), end="", flush=True)

	print("\r\n", end="", flush=True)
	return ret_str.decode("utf-8")

def on_exit(instagram):
	if (instagram.logged_in):
		if (instagram.logout()):
			print("{} Successfully logged out".format(SUCCESS))
		else:
			print("{} Failed to logout :/".format(ERROR))

def main():
	instagram = Instagram()
	atexit.register(on_exit, instagram)

	init() # Use Colorama to make Termcolor work on Windows too
	print("{} Reckless Instagram Target Turbo | Version 1.6 By t.de\r\n".format(SUCCESS))

	username = get_input("{} Username: ".format(INPUT)).strip()
	password = get_input("{} Password: ".format(INPUT), True)

	print("\r\n{} Attempting to login...".format(INFO))

	if (not instagram.login(username, password)):
		print("{} Failed to login - Check your password/account".format(ERROR))
		exit(1)
		
	print("{} Use one 1 Thread for long targeting 20 for swapping 3 for racing!".format(SUCCESS))
	threads = get_input("\r\n{} Threads: ".format(INPUT)).strip()
	instagram.target = get_input("{} Target: ".format(INPUT)).strip().lower()

	instagram.build_claim_data()
	print("{} Threads Succesfully initiated".format(SUCCESS))
	get_input("{} Ready. Press ENTER to start turbo!".format(SUCCESS))
	print("\x1b[A                                      \x1b[A")

	for i in range(int(threads)):
		thread = Turbo(instagram)
		thread.setDaemon(True)
		thread.start()

	rs_thread = RequestsPS(instagram)
	rs_thread.setDaemon(True)
	rs_thread.start()

	while (instagram.running):
		try:
			for spinner in ["|", "/", "-", "\\", "|", "/", "-", "\\"]:
				print("[\x1b[35m{}\x1b[39m] Turboing - {:,} attempts | {:,} r/s".format(spinner, instagram.attempts, instagram.rs), end="\r", flush=True)
				sleep(0.1) # Update attempts every 100ms
		except KeyboardInterrupt:
			print("\r{} Turbo stopped, exiting after {:,} attempts...\r\n".format(ERROR, instagram.attempts))
			break

	if (instagram.spam_blocked):
		print("\r{} Tried to claim @{} but account is spam blocked ({:,} attempts)\r\n".format(ERROR, instagram.target, instagram.attempts))

	elif (instagram.rate_limited):
		print("\r{} Rate limited after ({:,} attempts)\r\n".format(ERROR, instagram.attempts))

	elif (instagram.missed_swap):
		print("\r{} Missed username swap on @{} after {:,} attempts\r\n".format(ERROR, instagram.target, instagram.attempts))

	elif (instagram.claimed):
		print("\r{} Smoked  username @{} after {:,} attempts\r\n".format(SUCCESS, instagram.target, instagram.attempts))
		api = InstagramAPI('your.turbo', 'youclown')
		api.dm('Smoked username @{} after {} attempts'.format(instagram.target, instagram.attempts), 't.de')
		# api.dm('Smoked username @{} after {} attempts'.format(instagram.target, instagram.attempts), 'yourusername')

if (__name__ == "__main__"):
	main()