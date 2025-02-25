#!/usr/bin/env python3
# license-solver
# Copyright(C) 2021 Red Hat, Inc.
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Class download classifiers and extract data from them."""

import os
import re
import attr
import logging
from typing import List, Any

_LOGGER = logging.getLogger(__name__)


@attr.s(slots=True)
class Classifiers:
    """Class detect all classifiers from downloaded data."""

    received_text = attr.ib(init=False, type=str)
    classifiers: List[str] = attr.ib(init=True, default=list())
    classifiers_list: List[Any] = list()

    def __attrs_post_init__(self) -> None:
        """INIT method."""
        self._load_data()
        self._extract_classifiers()

    def _load_data(self) -> None:
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data/pypi_classifiers.txt")
        try:
            with open(file_path) as file:
                data = file.read()
                self.received_text = data
                _LOGGER.debug("File pypi_classifiers.txt was successful loaded")
        except OSError:
            _LOGGER.critical(f"Could not open/read file: {file_path}")
            raise OSError

    def _convert_to_list(self) -> None:
        """Covert downloaded string to list."""
        self.classifiers = list(self.received_text.split("\n"))

    def _extract(self) -> None:
        """Extract licence from classifiers list."""
        for classifier_full in self.classifiers:
            if len(classifier_full) >= 7 and classifier_full.startswith("License"):
                # append licenses to list
                classifier_name = self._get_name_license(classifier_full)
                classifier_abbreviation = self._get_abbreviation(classifier_full)

                li = list()
                li.append(classifier_full)  # full classifier name
                li.append(classifier_name)  # only name without "License :: ..."

                # abbreviation
                if len(classifier_abbreviation) > 0:
                    for abbre in classifier_abbreviation:
                        classifier_no_abbreviation = re.sub(" +", " ", classifier_name)
                        classifier_no_abbreviation = re.sub(" +", " ", classifier_no_abbreviation)
                        if classifier_name != classifier_no_abbreviation:
                            li.append(classifier_no_abbreviation)  # name without abbreviation

                        li.append(abbre)  # abbreviation
                        _x = abbre.replace("-", " ")
                        if _x != abbre:
                            li.append(_x)

                self.classifiers_list.append(li)

    def _extract_classifiers(self) -> None:
        """Extract classifiers from downloaded data."""
        self._convert_to_list()
        self._extract()

    @staticmethod
    def _get_name_license(classifier: str) -> str:
        """Get licence name from classifier string."""
        data = classifier.split("::")

        if len(data) > 0 and len(data[len(data) - 1]) > 1:
            return data[len(data) - 1].strip()[0:]
        else:
            return ""

    @staticmethod
    def _get_abbreviation(classifier: str) -> List[str]:
        """Abbreviation for license name."""
        abbreviation = list()
        start = classifier.find("(")
        end = classifier.find(")")
        if start != -1 and end != -1:
            txt = classifier[classifier.find("(") + 1 : classifier.find(")")]
            abbreviation.append(txt)
        return abbreviation
