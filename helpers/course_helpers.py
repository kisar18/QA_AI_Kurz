"""
Sdílené akce pro práci s kurzy (vytváření, navigace, registrace do kurzu).
"""

from playwright.sync_api import Page
from pages.courses_page import CoursesPage
from pages.course_create_page import CourseCreatePage


def create_course(
    page: Page,
    name: str,
    description: str = "",
    capacity: int = 15,
    price: int = 5000,
) -> CourseCreatePage:
    """Otevře stránku vytvoření kurzu a odešle formulář."""
    course_create_page = CourseCreatePage(page)
    course_create_page.navigate()
    course_create_page.create_course(
        name=name,
        description=description,
        capacity=capacity,
        price=price,
    )
    page.wait_for_load_state("networkidle")
    return course_create_page


def open_course_catalog(page: Page) -> CoursesPage:
    """Otevře katalog kurzů a počká na načtení."""
    courses_page = CoursesPage(page)
    courses_page.navigate()
    return courses_page
