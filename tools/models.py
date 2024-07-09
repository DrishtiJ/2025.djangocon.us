import datetime as pydatetime  # rename is needed because of yaml conflict
from typing import Literal

from pydantic import BaseModel
from slugify import slugify

import constants


class FrontmatterModel(BaseModel):
    """
    Our base class for our default "Frontmatter" fields.
    """

    layout: str | None = None
    permalink: str | None = None
    published: bool = True
    redirect_from: list[str] | None = None
    redirect_to: str | None = None  # via the jekyll-redirect-from plugin
    sitemap: bool | None = None
    title: str = ""

    class Config:
        extra = "allow"


class Social(BaseModel):
    github: str | None = None
    website: str | None = None
    mastodon: str | None = None
    twitter: str | None = None
    bluesky: str | None = None
    instagram: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.mastodon and self.mastodon.startswith("@"):
            self.mastodon = migrate_mastodon_handle(handle=self.mastodon)
            print(f"🚜 converting {self.mastodon=}")


class Organizer(FrontmatterModel):
    hidden: bool = False
    layout: str = "base"
    name: str
    photo: str | None = None
    slug: str | None = None
    title: str | None = None
    social: Social | None = None


class Page(FrontmatterModel):
    description: str | None = None
    heading: str | None = None
    hero_text_align: str | None = None  # homepage related
    hero_theme: str | None = None  # homepage related
    layout: str | None = None
    testimonial_img: str | None = None  # homepage related
    testimonial_img_mobile: str | None = None  # homepage related
    title: str | None = None


class Post(FrontmatterModel):
    author: str | None = None
    category: str | None = "General"  # TODO: build a list of these
    categories: list[str] | None = None
    date: pydatetime.datetime  # YYYY-MM-DD HH:MM:SS +/-TTTT
    image: str | None = None
    layout: str | None = "post"
    slug: str | None = None
    tags: list[str] | None = []


class Presenter(FrontmatterModel):
    company: str | None = None
    hidden: bool = False
    name: str
    override_schedule_title: str | None = None
    pronouns: str | None = None
    photo: str | None = None
    role: str | None = None
    slug: str | None = None
    social: Social | None = None

    def __init__(self, **data):
        super().__init__(**data)

        # if slugs are blank default them to slugify(name)
        if not self.slug:
            self.slug = slugify(self.name)

        # if permalink is blank, let's build a new one
        if not self.permalink:
            self.permalink = f"/presenters/{self.slug}/"


class Schedule(FrontmatterModel):
    accepted: bool = False
    category: Literal[
        "break",
        "lunch",
        "rooms",
        "social-event",
        "sprints",
        "talks",
        "tutorials",
    ]
    difficulty: str | None = "All"
    end_datetime: pydatetime.datetime | None = None
    group: None | (
        Literal[
            "break",
            "lunch",
            "rooms",
            "social-event",
            "sprints",
            "talks",
            "tutorials",
        ]
    ) = None

    image: str | None = None
    layout: str | None = "session-details"
    presenter_slugs: list[str] | None = None
    room: str | None = None
    show_video_urls: bool | None = None
    slides_url: str | None = None
    start_datetime: pydatetime.datetime | None
    tags: list[str] | None = None
    track: str | None = None
    video_url: str | None = None

    def __init__(self, **data):
        super().__init__(**data)

        # TODO check with Michael if we still need both group and category
        if self.group != self.category:
            self.group = self.category


class ManualScheduleEntry(BaseModel):
    datetime: pydatetime.datetime
    end_datetime: pydatetime.datetime
    group: Literal[
        "break",
        "lunch",
        "rooms",
        "social-event",
        "sprints",
        "talks",
        "tutorials",
    ]
    permalink: str | None
    room: str
    title: str
    track: str = "t0"
    abstract: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.abstract:
            self.abstract = self.room


def migrate_mastodon_handle(*, handle: str) -> str:
    if not handle.startswith("@"):
        return handle

    username, domain = handle[1:].split("@")
    return f"https://{domain}/@{username}"


MANUAL_SCHEDULE_ENTRIES = [
    # Sunday breakfast
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(9),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#sunday-breakfast",
        room=constants.LUNCH_ROOM,
        title="Continental Breakfast",
        track="t0",
    ),
    # TODO decide whether we'll have quiet/lactation rooms on tutorial day
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(18),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=f"In front of {constants.LARGE_TALK_ROOM}",
        title="Registration",
        track="t0",
    ),
    # sunday lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(12, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TUTORIAL_DAY,
            pydatetime.time(13, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#sunday-lunch",
        room=constants.LUNCH_ROOM,
        title="Lunch",
        track="t0",
    ),
    # Monday!
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(7, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(8, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#monday-breakfast",
        room=constants.LUNCH_ROOM,
        title="Continental Breakfast",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(7, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=f"In front of {constants.LARGE_TALK_ROOM}",
        title="Registration",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/news/childcare-lactation/",
        room=constants.LACTATION_ROOM,
        title="Lactation Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.QUIET_ROOM,
        title="Quiet Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.GREEN_ROOM,
        title="Speaker Green Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(10, 10),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(10, 35),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#monday-morning-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # monday early lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(12, 0),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#monday-lunch",
        room=constants.LUNCH_ROOM,
        title="Early Lunch",
        track="t0",
    ),
    # monday main lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            # NOTE this must match the length of the online talk
            pydatetime.time(13, 25),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#monday-lunch",
        room=constants.LUNCH_ROOM,
        title="Lunch",
        track="t0",
    ),
    # monday PM break
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(14, 55),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(15, 20),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#monday-morning-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # board game night
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(19),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_1,
            pydatetime.time(22),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,  # TODO add social link here
        room=constants.LARGE_TALK_ROOM,
        title="Board Game Night",
        track="t0",
    ),
    # Tuesday!
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(9),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#tuesday-breakfast",
        room=constants.LUNCH_ROOM,
        title="Continental Breakfast",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=f"In front of {constants.LARGE_TALK_ROOM}",
        title="Registration",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/news/childcare-lactation/",
        room=constants.LACTATION_ROOM,
        title="Lactation Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.QUIET_ROOM,
        title="Quiet Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.GREEN_ROOM,
        title="Speaker Green Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(10, 10),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(10, 35),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#tuesday-morning-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # tuesday early lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(12, 0),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#tuesday-lunch",
        room=constants.LUNCH_ROOM,
        title="Early Lunch",
        track="t0",
    ),
    # tuesday main lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            # NOTE this must match the length of the online talk
            pydatetime.time(13, 25),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#monday-lunch",
        room=constants.LUNCH_ROOM,
        title="Lunch",
        track="t0",
    ),
    # tuesday PM break
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(14, 55),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_2,
            pydatetime.time(15, 20),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#tuesday-afternoon-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # Wednesday!
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(9),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#wednesday-breakfast",
        room=constants.LUNCH_ROOM,
        title="Continental Breakfast",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=f"In front of {constants.LARGE_TALK_ROOM}",
        title="Registration",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/news/childcare-lactation/",
        room=constants.LACTATION_ROOM,
        title="Lactation Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.QUIET_ROOM,
        title="Quiet Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(8),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(17, 30),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink=None,
        room=constants.GREEN_ROOM,
        title="Speaker Green Room",
        track="t0",
    ),
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(10, 10),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(10, 35),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#wednesday-morning-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # wed early lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(12, 0),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#wednesday-lunch",
        room=constants.LUNCH_ROOM,
        title="Early Lunch",
        track="t0",
    ),
    # wed main lunch
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(12, 40),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            # NOTE this must match the length of the online talk
            pydatetime.time(13, 25),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="lunch",
        permalink="/catering-menus/#wednesday-lunch",
        room=constants.LUNCH_ROOM,
        title="Lunch",
        track="t0",
    ),
    # wed PM break
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(14, 55),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.TALK_DAY_3,
            pydatetime.time(15, 20),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="break",
        permalink="/catering-menus/#wednesday-afternoon-break",
        room=constants.LUNCH_ROOM,
        title="Break",
        track="t0",
    ),
    # Thursday!
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.SPRINTS_DAY_1,
            pydatetime.time(9),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.SPRINTS_DAY_1,
            pydatetime.time(17),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="talks",
        permalink=None,
        room="Caktus Group",
        title="Contribution Sprints",
        track="t0",
    ),
    # Friday!
    ManualScheduleEntry(
        datetime=pydatetime.datetime.combine(
            constants.SPRINTS_DAY_2,
            pydatetime.time(9),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        end_datetime=pydatetime.datetime.combine(
            constants.SPRINTS_DAY_2,
            pydatetime.time(17),
            tzinfo=constants.CONFERENCE_TZ,
        ),
        group="talks",
        permalink=None,
        room="Caktus Group",
        title="Contribution Sprints",
        track="t0",
    ),
]
