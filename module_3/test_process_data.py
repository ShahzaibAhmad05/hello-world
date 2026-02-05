import pytest
from module_3.process_data import process_data

def test_process_data_basic():
    """Test basic functionality with active and inactive items"""
    data = [
        {'status': 'active', 'value': 5},
        {'status': 'inactive', 'value': 10},
        {'status': 'active', 'value': 3}
    ]
    assert process_data(data) == [10, 6]


def test_process_data_all_active():
    """Test with all items having active status"""
    data = [
        {'status': 'active', 'value': 2},
        {'status': 'active', 'value': 4},
        {'status': 'active', 'value': 6}
    ]
    assert process_data(data) == [4, 8, 12]


def test_process_data_all_inactive():
    """Test with all items having inactive status"""
    data = [
        {'status': 'inactive', 'value': 5},
        {'status': 'inactive', 'value': 10}
    ]
    assert process_data(data) == []


def test_process_data_empty_list():
    """Test with an empty list"""
    assert process_data([]) == []


def test_process_data_zero_values():
    """Test with active items having zero values"""
    data = [
        {'status': 'active', 'value': 0},
        {'status': 'active', 'value': 5}
    ]
    assert process_data(data) == [0, 10]


def test_process_data_negative_values():
    """Test with negative values"""
    data = [
        {'status': 'active', 'value': -5},
        {'status': 'active', 'value': 3}
    ]
    assert process_data(data) == [-10, 6]


def test_process_data_missing_value_key():
    """Test with items missing the value key"""
    data = [
        {'status': 'active'},
        {'status': 'active', 'value': 5}
    ]
    assert process_data(data) == [10]


def test_process_data_missing_status_key():
    """Test with items missing the status key"""
    data = [
        {'value': 5},
        {'status': 'active', 'value': 3}
    ]
    assert process_data(data) == [6]


def test_process_data_invalid_type():
    """Test with invalid item types"""
    data = [
        None,
        {'status': 'active', 'value': 5},
        "invalid"
    ]
    assert process_data(data) == [10]


def test_process_data_float_values():
    """Test with float values"""
    data = [
        {'status': 'active', 'value': 2.5},
        {'status': 'active', 'value': 1.5}
    ]
    assert process_data(data) == [5.0, 3.0]


def test_process_data_case_sensitive_status():
    """Test that status matching is case-sensitive"""
    data = [
        {'status': 'Active', 'value': 5},
        {'status': 'ACTIVE', 'value': 3},
        {'status': 'active', 'value': 2}
    ]
    assert process_data(data) == [4]


def test_process_data_non_numeric_value():
    """Test with non-numeric values"""
    data = [
        {'status': 'active', 'value': 'not_a_number'},
        {'status': 'active', 'value': 5}
    ]
    assert process_data(data) == [10]
    