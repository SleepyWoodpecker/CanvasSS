from playwright.sync_api import sync_playwright, Playwright, BrowserContext
import os

LOGIN_DETAILS_PATH = "bruin_one_login_state.json"
LOADING_TIMEOUT = 5000


def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)

    if not os.path.exists(LOGIN_DETAILS_PATH):
        login_context = browser.new_context()
        login(context=login_context)
        login_context.close()

    context = browser.new_context(storage_state=LOGIN_DETAILS_PATH)

    page = context.new_page()
    page.goto(
        "https://ucla.vitalsource.com/reader/books/9781319055844/epubcfi/6/328[%3Bvnd.vst.idref%3Drog_9781319050733_answer_ch01]!/4"
    )

    page.wait_for_timeout(LOADING_TIMEOUT)

    # this produces a result, just need to check how I should be converting this result into something that I can make use of afterwards
    iframe = (
        page.frame_locator("[title='Document reading pane']")
        .frame_locator(".favre")
        .locator("body")
        .element_handle()
    )


def login(context: BrowserContext):
    page = context.new_page()
    page.goto("https://bc.vitalsource.com/tenants/212287/saml_auth/materials")
    # I think the only way to get the login token is to do a manual login
    page.wait_for_timeout(45000)
    context.storage_state(path=LOGIN_DETAILS_PATH)
    page.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
