from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


DOF_URL = "https://www.dof.gob.mx/"
SEARCH_AREAS = (
    "tesoreria",
    "juridico",
    "contraloria",
    "contabilidad",
    "banco de mexico",
    "sistemas",
    "banca",
    "finanzas",
)


def download_documents_since(browser, area: str, minimum_year: int) -> None:
    search_box = browser.find_element(By.NAME, "textobusqueda")
    search_box.clear()
    search_box.send_keys(area + Keys.RETURN)
    sleep(5)

    while True:
        previous_pages = browser.find_elements(By.XPATH, "//img[@alt='anterior']")
        if not previous_pages:
            break
        previous_pages[0].click()
        sleep(3)

    while True:
        document_links = browser.find_elements(
            By.XPATH,
            "//td[@class='txt_azul']//a[contains(@href, '/nota_to_doc.php?codnota=')]",
        )
        matching_documents = False
        for document_link in document_links:
            date_text = document_link.find_element(
                By.XPATH,
                "../../td[@class='txt_azul']/b",
            ).text
            if datetime.strptime(date_text, "%d/%m/%Y").year >= minimum_year:
                matching_documents = True
                document_link.click()
                sleep(2)

        if not matching_documents:
            break

        next_pages = browser.find_elements(By.XPATH, "//img[@alt='siguiente']")
        if not next_pages:
            break
        next_pages[0].click()
        sleep(3)


def download_documents() -> None:
    browser = webdriver.Chrome()
    try:
        browser.get(DOF_URL)
        sleep(5)
        for area in SEARCH_AREAS:
            download_documents_since(browser, area, minimum_year=2022)
    finally:
        browser.quit()


if __name__ == "__main__":
    download_documents()
