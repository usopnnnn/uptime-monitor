import uiautomator2 as u2
import time
import random
import logging
import os
from datetime import datetime

# Screenshots Directory Check
SCREENSHOTS_DIR = "screenshots"
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logfile.log"),
        logging.StreamHandler()
    ]
)

# Screenshot Function
def take_screenshot(d, name_prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_prefix}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    try:
        d.screenshot(filepath)
        logging.info(f"Screenshot saved to {filepath}")
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
    return filepath

# Delay Function
def random_delay(min_seconds=30, max_seconds=120):
    delay = random.uniform(min_seconds, max_seconds)
    logging.info(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)

# Load Configuration
try:
    import config
except ImportError:
    logging.error("config.py not found. Please ensure it exists and is correctly formatted.")
    exit()

# Placeholder for main bot logic
if __name__ == "__main__":
    logging.info("Instagram Bot MVP started.")
    d = None  # Initialize d to None
    try:
        # --- ADB and Device Setup ---
        logging.info("Attempting to connect to Android device...")
        # Add comments for user: Ensure ADB is running and device is connected via USB with USB debugging enabled.
        # Example: adb devices - if no device listed, check connection and developer options.
        d = u2.connect()  # Connects to the first available device or emulator
        if not d.device_info:
            logging.error("Failed to connect to any device. Is a device/emulator connected and authorized?")
            exit()

        logging.info(f"Successfully connected to device: {d.device_info.get('serial')}")
        logging.info("Device screen resolution: {}x{}".format(d.info['displayWidth'], d.info['displayHeight']))
        # Wake up the device and unlock if necessary (basic attempt)
        d.screen_on()
        # d.swipe(0.5, 0.8, 0.5, 0.2) # Example swipe to unlock if needed, may require adjustment

        # --- Launch Instagram ---
        logging.info("Launching Instagram...")
        d.app_start("com.instagram.android", use_monkey=True)
        random_delay(5, 10) # Wait for app to load

        # --- Authentication ---
        # Check if already logged in. This is a basic check, might need adjustment.
        # Looking for a common element on the home screen, e.g., home icon or stories.
        # This selector might need to be made more robust.
        # Common selectors for elements on the Instagram home screen (these can vary):
        # - Home icon: resourceId="com.instagram.android:id/tab_bar_home_button"
        # - Stories reel: resourceId="com.instagram.android:id/stories_tray_container"
        # - New post button: resourceId="com.instagram.android:id/tab_bar_creation_button"

        # Try to find a common element that indicates user is logged in
        if d(resourceId="com.instagram.android:id/tab_bar_home_button").exists(timeout=10):
            logging.info("User already logged in.")
            take_screenshot(d, "already_logged_in")
        else:
            logging.info("User not logged in or login state unclear. Attempting login.")
            # Look for login button or username field
            # Selector for "Log in" button on the initial screen (if present)
            if d(text="Log in", resourceId="com.instagram.android:id/log_in_button").exists(timeout=5):
                d(text="Log in", resourceId="com.instagram.android:id/log_in_button").click()
                random_delay(2,4)

            # Username field selector
            username_field_selector = "com.instagram.android:id/login_username"
            # Password field selector
            password_field_selector = "com.instagram.android:id/password"
            # Login button selector (after entering credentials)
            login_button_selector = "com.instagram.android:id/next_button" # Often labeled as "Log In" or "Next"

            if d(resourceId=username_field_selector).exists(timeout=5):
                logging.info("Entering username...")
                d(resourceId=username_field_selector).set_text(config.INSTAGRAM_USERNAME)
                random_delay(1,2)

                logging.info("Entering password...")
                d(resourceId=password_field_selector).set_text(config.INSTAGRAM_PASSWORD)
                random_delay(1,2)

                logging.info("Clicking login button...")
                if d(resourceId=login_button_selector).exists():
                    d(resourceId=login_button_selector).click()
                else:
                    logging.error("Login button not found after entering credentials.")
                    raise Exception("Login button not found")

                random_delay(10, 15) # Wait for login to complete and home screen to load

                # Verify login success
                if d(resourceId="com.instagram.android:id/tab_bar_home_button").exists(timeout=15):
                    logging.info("Login successful!")
                    take_screenshot(d, "login_successful")
                else:
                    # Handle common login issues like "Save login info?" pop-up
                    if d(textContains="Save your login info?").exists(timeout=5):
                        logging.info("Handling 'Save login info?' pop-up...")
                        # Option 1: Click "Not Now" or equivalent
                        if d(text="Not now", resourceId="com.instagram.android:id/button_negative").exists():
                             d(text="Not now", resourceId="com.instagram.android:id/button_negative").click()
                             random_delay(3,5)
                        elif d(text="Save").exists() and d(text="Not Now").exists(): # Some dialogs have both
                            # Heuristic: "Not Now" is usually what we want for automation
                            # This part may need refinement based on actual dialogs
                            elements = d(className="android.widget.Button")
                            for el in elements:
                                if "not now" in el.info['text'].lower():
                                    el.click()
                                    random_delay(3,5)
                                    break
                        if d(resourceId="com.instagram.android:id/tab_bar_home_button").exists(timeout=10):
                             logging.info("Login successful after handling pop-up.")
                             take_screenshot(d, "login_successful_after_popup")
                        else:
                            logging.error("Login failed even after attempting to handle pop-up.")
                            take_screenshot(d, "login_failed_after_popup")
                            raise Exception("Login failed")
                    else:
                        logging.error("Login failed. Home screen element not found.")
                        take_screenshot(d, "login_failed")
                        raise Exception("Login failed")
            else:
                logging.warning("Login fields not found. Assuming already logged in or on an unexpected screen.")
                # Take a screenshot for debugging if login fields are not immediately visible
                take_screenshot(d, "login_fields_not_found")
                if not d(resourceId="com.instagram.android:id/tab_bar_home_button").exists(timeout=5):
                    logging.error("Still not on home screen after assuming login. Exiting.")
                    raise Exception("Login state unclear and not on home screen")

        # --- Navigate to Target Profile ---
        target_username = config.TARGET_ACCOUNTS[0]
        logging.info(f"Navigating to profile: {target_username}")

        # Click search tab icon (common selector)
        # Some versions might use content-desc="Search and explore"
        search_tab_selector_id = "com.instagram.android:id/search_tab"
        # Fallback if the above ID changes, based on common layouts
        search_tab_selector_xpath = '//*[@resource-id="com.instagram.android:id/tab_bar"]/android.widget.FrameLayout[2]'

        if d(resourceId=search_tab_selector_id).exists(timeout=5):
            d(resourceId=search_tab_selector_id).click()
        elif d.xpath(search_tab_selector_xpath).exists():
            d.xpath(search_tab_selector_xpath).click()
        else:
            logging.error("Search tab icon not found.")
            raise Exception("Search tab icon not found")

        random_delay(2, 4)

        # Click search bar (often a text input field at the top)
        # Common resourceId for search bar input area
        search_bar_selector_id = "com.instagram.android:id/action_bar_search_edit_text"
        # Alternative: sometimes it's a general "Search" text input
        search_bar_selector_text = "Search"

        if d(resourceId=search_bar_selector_id).exists(timeout=5):
            d(resourceId=search_bar_selector_id).click()
            random_delay(1,2)
            d(resourceId=search_bar_selector_id).set_text(target_username)
        elif d(text=search_bar_selector_text, className="android.widget.EditText").exists(timeout=5):
            d(text=search_bar_selector_text, className="android.widget.EditText").click()
            random_delay(1,2)
            d(text=search_bar_selector_text, className="android.widget.EditText").set_text(target_username)
        else:
            logging.error("Search bar input field not found.")
            # Attempt to type directly if focus might already be there (less reliable)
            logging.info("Attempting to type target username directly...")
            d.set_fastinput_ime(True) # Use fast input method
            d.send_keys(target_username)
            d.set_fastinput_ime(False) # Reset IME
            # This direct send_keys might not work if a field isn't focused.
            # Further checks needed if this path is taken often.

        random_delay(3, 6) # Wait for search results

        # Click on the target user from search results
        # This usually involves finding the username in a list.
        # Selector might be complex, often text=target_username inside a specific layout for user results.
        # Example: d(resourceId="com.instagram.android:id/row_search_user_username", text=target_username)
        # For robustness, we might need to iterate through results if the direct selector is flaky.
        # A common container for user search results: com.instagram.android:id/user_list_container

        # Click the first user result that matches the username, usually the most relevant.
        # This selector looks for a layout containing the username and their display name.
        user_profile_link_selector = f'//*[@resource-id="com.instagram.android:id/recycler_view"]//android.widget.TextView[@text="{target_username}"]'

        if d.xpath(user_profile_link_selector).exists(timeout=10):
            d.xpath(user_profile_link_selector).click()
            logging.info(f"Clicked on user profile: {target_username}")
        else:
            logging.error(f"Could not find user {target_username} in search results with primary selector.")
            # Fallback: try clicking based on text if the specific structure above fails
            if d(text=target_username).exists(timeout=5):
                d(text=target_username).click() # This might be less precise
                logging.info(f"Clicked on user profile (fallback by text): {target_username}")
            else:
                take_screenshot(d, "target_profile_not_found_in_search")
                raise Exception(f"Target profile {target_username} not found in search results")

        random_delay(5, 8) # Wait for profile to load
        take_screenshot(d, f"profile_{target_username}")

        # --- Follow User ---
        # Common "Follow" button selectors
        follow_button_text = "Follow"
        follow_button_id_v1 = "com.instagram.android:id/profile_header_follow_button" # Older ID
        follow_button_id_v2 = "com.instagram.android:id/profile_header_actions_follow_button" # Newer ID
        # Sometimes it's a Button class with text "Follow"

        followed = False
        if d(resourceId=follow_button_id_v2, text=follow_button_text).exists(timeout=5):
            d(resourceId=follow_button_id_v2, text=follow_button_text).click()
            followed = True
        elif d(resourceId=follow_button_id_v1, text=follow_button_text).exists(timeout=5):
            d(resourceId=follow_button_id_v1, text=follow_button_text).click()
            followed = True
        elif d(text=follow_button_text, className="android.widget.Button").exists(timeout=5):
            d(text=follow_button_text, className="android.widget.Button").click()
            followed = True
        elif d(text="Following").exists(timeout=2): # Check if already following
            logging.info(f"Already following {target_username}.")
            followed = True # Treat as success for the purpose of the demo
        else:
            logging.warning(f"Follow button not found for {target_username} with primary selectors. May already be following or UI changed.")
            take_screenshot(d, f"follow_button_not_found_{target_username}")
            # For MVP, we'll log a warning. In a real bot, might raise error or try other selectors.

        if followed:
            logging.info(f"Follow action performed for {target_username} (or already following).")
            take_screenshot(d, f"followed_{target_username}")

        random_delay() # Random delay after follow action

        # --- Like Posts ---
        logging.info(f"Attempting to like the two most recent posts for {target_username}.")
        # Posts are usually in a RecyclerView or similar grid.
        # The first post is typically the first clickable item in the grid/feed area.
        # Selector for the main content area (often a RecyclerView or ViewPager)
        # This needs to be general enough to find the posts area.
        # Common parent of posts: com.instagram.android:id/recycler_view or a ViewPager
        # Individual posts might be FrameLayout or LinearLayout elements.

        # Assuming posts are listed vertically, the first few children of the main feed/grid view
        # This is a common structure for post items.
        # We need to find clickable elements that represent posts.
        # A common pattern is that posts are children of a RecyclerView.
        posts_container_selector = d(resourceId="androidx.recyclerview.widget.RecyclerView").child(className="android.widget.LinearLayout") # This will get multiple

        # More specific post selector within a known grid/list structure:
        # This XPath tries to find the first two direct children of the main content area that are likely posts.
        # The actual structure can vary significantly.
        # This selector assumes posts are direct children of a known container.
        # It looks for elements that are likely to be posts (e.g., FrameLayouts within a RecyclerView)
        # This is highly dependent on the current Instagram UI version.

        # Let's try a simpler approach: find the first clickable items in the grid.
        # Posts are usually located in the third row of elements on a profile page (after bio, highlights, etc.)
        # This is a heuristic and might need adjustment.
        # A common content description for a post might be "Photo by [username]" or "Video by [username]"

        # Try to get all image views in the main content area, assuming they are posts.
        # This is a common way posts are displayed in the grid.
        # The `row_feed_photo_imageview` or similar ID is often used for the main image of a post in the grid.
        post_image_selector_id = "com.instagram.android:id/row_feed_photo_imageview" # Grid view image

        # Generic post item selector: First level children of the RecyclerView are often posts
        # This XPath assumes a RecyclerView contains post items directly or within one level of nesting.
        # It targets the first two such items.
        post_xpath_template = '(//*[@resource-id="com.instagram.android:id/recycler_view"]/*/*[@clickable="true"])[{}]'
        # If the above is too broad, a more specific one might be needed, e.g., targeting FrameLayouts:
        # post_xpath_template = '(//*[@resource-id="com.instagram.android:id/recycler_view"]//android.widget.FrameLayout[@clickable="true"])[{}]'

        liked_posts_count = 0
        for i in range(1, 3): # Try to like 2 posts
            logging.info(f"Attempting to open post #{i}...")
            post_selector = d.xpath(post_xpath_template.format(i))

            if post_selector.exists(timeout=10):
                post_selector.click()
                random_delay(5, 8) # Wait for post to open
                take_screenshot(d, f"opened_post_{i}_{target_username}")

                # Like the post
                # Common like button selectors:
                # - resourceId="com.instagram.android:id/row_feed_button_like" (heart icon before liking)
                # - resourceId="com.instagram.android:id/row_feed_button_liked" (red heart icon after liking)
                # - content-desc="Like"
                like_button_selector_id = "com.instagram.android:id/row_feed_button_like"
                like_button_selector_desc = "Like"

                # Check if already liked (red heart)
                if d(resourceId="com.instagram.android:id/row_feed_button_liked").exists():
                    logging.info(f"Post #{i} is already liked.")
                elif d(resourceId=like_button_selector_id).exists(timeout=5):
                    d(resourceId=like_button_selector_id).click()
                    logging.info(f"Liked post #{i}.")
                    take_screenshot(d, f"liked_post_{i}_{target_username}")
                    liked_posts_count += 1
                elif d(description=like_button_selector_desc).exists(timeout=5): # Fallback by content description
                    d(description=like_button_selector_desc).click()
                    logging.info(f"Liked post #{i} (using content-desc).")
                    take_screenshot(d, f"liked_post_{i}_{target_username}_desc")
                    liked_posts_count += 1
                else:
                    logging.warning(f"Like button not found for post #{i}. It might be a video with different controls or UI changed.")
                    take_screenshot(d, f"like_button_not_found_post_{i}_{target_username}")

                random_delay(2, 4)
                d.press("back") # Go back to profile/grid
                random_delay(3, 5) # Wait to return to profile
            else:
                logging.warning(f"Could not find post #{i} using XPath. Post grid structure might have changed.")
                take_screenshot(d, f"post_{i}_not_found_{target_username}")
                break # Stop if posts cannot be found

        if liked_posts_count > 0:
            random_delay() # Random delay after liking posts

        # --- Comment on the Most Recent Post (Post #1) ---
        if liked_posts_count > 0 or d.xpath(post_xpath_template.format(1)).exists(): # Only comment if we could interact or find the first post
            logging.info(f"Attempting to comment on the most recent post for {target_username}.")

            # Re-open the first post
            post_selector = d.xpath(post_xpath_template.format(1))
            if post_selector.exists(timeout=10):
                post_selector.click()
                random_delay(5, 8) # Wait for post to open

                # Click comment button
                # Common comment button selectors:
                # - resourceId="com.instagram.android:id/row_feed_button_comment"
                # - content-desc="Comment"
                comment_button_selector_id = "com.instagram.android:id/row_feed_button_comment"
                comment_button_selector_desc = "Comment"

                if d(resourceId=comment_button_selector_id).exists(timeout=5):
                    d(resourceId=comment_button_selector_id).click()
                elif d(description=comment_button_selector_desc).exists(timeout=5):
                    d(description=comment_button_selector_desc).click()
                else:
                    logging.error("Comment button not found.")
                    take_screenshot(d, f"comment_button_not_found_{target_username}")
                    raise Exception("Comment button not found")

                random_delay(3, 5) # Wait for comment input field to appear

                # Type comment
                comment_text_field_selector_id = "com.instagram.android:id/layout_comment_thread_edittext" # Common ID for comment input

                if d(resourceId=comment_text_field_selector_id).exists(timeout=5):
                    comment_to_post = random.choice(config.COMMENT_TEMPLATES)
                    logging.info(f"Typing comment: '{comment_to_post}'")
                    d(resourceId=comment_text_field_selector_id).set_text(comment_to_post)
                    random_delay(2, 4)

                    # Click post/send comment button
                    # Common post comment button selectors:
                    # - resourceId="com.instagram.android:id/layout_comment_thread_post_button_click_area"
                    # - text="Post"
                    post_comment_button_selector_id = "com.instagram.android:id/layout_comment_thread_post_button_click_area"
                    post_comment_button_text = "Post"

                    if d(resourceId=post_comment_button_selector_id).exists(timeout=5):
                        d(resourceId=post_comment_button_selector_id).click()
                    elif d(text=post_comment_button_text, className="android.widget.Button").exists(timeout=5): # Often a button with text "Post"
                        d(text=post_comment_button_text, className="android.widget.Button").click()
                    else:
                        logging.error("Post comment button not found.")
                        take_screenshot(d, f"post_comment_button_not_found_{target_username}")
                        # Attempt to send by pressing enter on keyboard if applicable (less reliable)
                        # d.press("enter")
                        raise Exception("Post comment button not found")

                    logging.info(f"Commented: '{comment_to_post}' on the most recent post.")
                    take_screenshot(d, f"commented_post_{target_username}")
                    random_delay(3, 5)

                    d.press("back") # Back from comment screen
                    random_delay(1,2)
                    d.press("back") # Back from post view to profile
                    random_delay(1,2)

                else:
                    logging.error("Comment input field not found.")
                    take_screenshot(d, f"comment_field_not_found_{target_username}")
                    # Go back if comment field wasn't found to avoid getting stuck
                    d.press("back")
                    random_delay(1,2)
                    d.press("back")
            else:
                logging.warning("Could not re-open first post to comment. Skipping comment action.")
                take_screenshot(d, f"first_post_not_reopened_for_comment_{target_username}")
        else:
            logging.info("Skipping comment action as no posts were successfully liked or found.")

        random_delay() # Final delay before finishing

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if d: # if device object 'd' exists
            take_screenshot(d, "error_occurred")
    finally:
        if d:
            logging.info("Closing Instagram app.")
            d.app_stop("com.instagram.android")
        logging.info("Instagram Bot MVP finished.")
