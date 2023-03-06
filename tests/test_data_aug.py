#!/usr/bin/env python

"""Tests for `data_aug` package."""

from data_aug.data_aug import sample


def test_sample():
    assert sample(True)
    assert not sample(False)
