from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
import os, json


def run(playwright: Playwright, config: dict[str, str | int]) -> None:
    """
    Runs the main screenshotting script

    Parameters:
        playwright - the playwright object, preferably passed in by context
    """
    firefox = playwright.firefox
    browser = firefox.launch(headless=True)

    if not os.path.exists(config["login_details_path"]):
        login_context = browser.new_context()
        login(context=login_context)
        login_context.close()

    context = browser.new_context(
        storage_state=config["login_details_path"],
        viewport={"height": 1300, "width": 1500},
    )

    page = context.new_page()
    page.goto(config["textbook_url"])

    page.wait_for_selector("button[aria-label*='ANS'][aria-label~='Chapter']")

    for chapter_button in page.query_selector_all(
        "button[aria-label*='ANS'][aria-label~='Chapter']"
    ):
        # load the iframe for the chapter
        chapter_button.click()
        page.wait_for_timeout(config["timeout"]["chapter_loading"])
        chapter_name = chapter_button.query_selector("span").inner_text()
        print(f"Currently at {chapter_name}...")

        # this produces a result, just need to check how I should be converting this result into something that I can make use of afterwards
        iframe_body = (
            page.frame_locator("[title='Document reading pane']")
            .frame_locator(".favre")
            .locator("body")
            .element_handle()
        )
        iframe_body.click()

        initial_next_button_classes = get_next_button_classes(page=page)

        chapter_image_counter = 1
        while not at_end_of_page(
            page=page, initial_next_button_classes=initial_next_button_classes
        ):
            # give page some time to load
            page.wait_for_timeout(config["timeout"]["default"])
            page.screenshot(
                path=f"{config['output_folder_name']}/{chapter_name}/Answer Page {chapter_image_counter}.png",
                full_page=True,
            )

            # trialed and errored to take 1000 as a reasonable page size
            page.mouse.wheel(0, 1000)
            chapter_image_counter += 1


def login(context: BrowserContext, config: dict[str, str | int]) -> None:
    """
    Generates and saves the log in cookies so that the user only need log in once

    @param context: a new browser context to perform the login on
    """
    page = context.new_page()
    page.goto(config["login_url"])
    # I think the only way to get the login token is to do a manual login
    page.wait_for_timeout(config["timeout"]["login"])
    context.storage_state(path=config["login_details_path"])
    page.close()


def at_end_of_page(page: Page, initial_next_button_classes: str) -> bool:
    """
    Checks if the answer sheet has been scrolled to the bottom of the page. Whether or not you are at the end of the page is determined by if the 'next' button changes it color and hence class

    Parameters:
        page - the page object that is currently at the answer sheet page
        initial_next_button_class - original string representation of the 'next' button's class

    Return:
        A boolean indicating if the last section of the answer sheet is inside the viewport
    """
    return get_next_button_classes(page=page) != initial_next_button_classes


def get_next_button_classes(page: Page) -> str:
    """
    Get the string representation of the classes that the 'Next' button has

    Parameters:
        page - the page object that is currently at the answer sheet page

    Return:
        A string that contains all the classes that the 'Next' button currently has
    """
    next_button = page.query_selector("button[aria-label='Next']")
    return next_button.get_attribute("class")


if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

        os.makedirs(name=config["output_folder_name"], exist_ok=True)

        with sync_playwright() as playwright:
            run(playwright, config=config)
