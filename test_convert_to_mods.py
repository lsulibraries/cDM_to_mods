#! /usr/bin/env python3

# import pytest
# from mock import patch
import convert_to_mods


def test_parse_dates():
    assert convert_to_mods.parse_dates('') == ''
    assert convert_to_mods.parse_dates('1750') == '1750'
    assert convert_to_mods.parse_dates('1950s') == '1950s'
    assert convert_to_mods.parse_dates('Christmas 1995') == 'Christmas 1995'
    assert convert_to_mods.parse_dates('around 1940') == 'around 1940'
    assert convert_to_mods.parse_dates('jan 5, 1943') == '1943-01-05'
    assert convert_to_mods.parse_dates('1940 jun 3') == '1940-06-03'
    assert convert_to_mods.parse_dates('1923 6 mar') == '1923-03-06'
    assert convert_to_mods.parse_dates('1976 Spring') == '1976 Spring'
    assert convert_to_mods.parse_dates('[1750]') == '[1750]'
    assert convert_to_mods.parse_dates('[1750-05-17]') == '[1750-05-17]'
    assert convert_to_mods.parse_dates('[unknown]') == '[unknown]'
    assert convert_to_mods.parse_dates('[ca. 1750] ') == '[ca. 1750]'
    assert convert_to_mods.parse_dates('[1750-01]') == '[1750-01]'
    assert convert_to_mods.parse_dates('[1750 august 23]') == '[1750-08-23]'
    assert convert_to_mods.parse_dates('[1913?]') == '[1913?]'
    assert convert_to_mods.parse_dates('1913?') == '1913?'
    assert convert_to_mods.parse_dates('[192?]') == '[192?]'
