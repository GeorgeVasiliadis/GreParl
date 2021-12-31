from dataclasses import dataclass
from datetime import date

@dataclass
class MockSpeech:
    """
    A speech in parliament with its metadata.
    """
    member_name: str
    sitting_date: date
    parliamentary_period: int
    parliamentary_session: int
    parliamentary_sitting: int
    political_party: str
    government: str
    member_region: str
    roles: list[str]
    gender: str
    contents: str
    id: int = 0

    def title(self):
        """Return the first sentence of the speech that ends with a period (.) in
        title case. If there is no such sentence, return "Untitled Speech"
        """
        title = self.contents.split(".")[0].title()
        return title if title else "Untitled Speech"

    def description(self, max=250):
        """Return the first words of the speech, without exceeding the `max`
        characters limit. If the speech is less than `max` characters, the
        whole speech is returned.
        """

        if len(self.contents) <= max:
            description = self.contents
        else:
            description = self.contents[:max].rsplit(" ", 1)[0]

        return description

mock_speech = MockSpeech(
    "Real Name",
    date.today(),
    100,
    5,
    26,
    "Real Party Name",
    "Government Name",
    "Member Region",
    "Role1 Role2 Role3 Role4".split(),
    "Male",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent varius ac risus id hendrerit. Vivamus non urna eu nulla consectetur facilisis at ac sapien. Quisque elit tortor, tempor maximus velit vitae, vestibulum gravida tellus. Vivamus pulvinar diam ac dui tempus bibendum. Aenean congue ac mauris eu mattis. Suspendisse potenti. Sed egestas rhoncus sapien eget ultricies. Aliquam in leo in orci pretium pretium ut ut sem.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent varius ac risus id hendrerit. Vivamus non urna eu nulla consectetur facilisis at ac sapien. Quisque elit tortor, tempor maximus velit vitae, vestibulum gravida tellus. Vivamus pulvinar diam ac dui tempus bibendum. Aenean congue ac mauris eu mattis. Suspendisse potenti. Sed egestas rhoncus sapien eget ultricies. Aliquam in leo in orci pretium pretium ut ut sem.",
    10
)
