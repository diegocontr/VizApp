import pytest
from modelviz.keygen import key_generator, reverse_key_generator, get_hierarchical_parameter_options, get_all_distinct_parameter_values


# --- Test Data Fixtures ---
@pytest.fixture
def sample_plot_data_preserved_types():
    """Sample dict_of_all_plots with preserved types."""
    params1 = {'dataset': 'Alpha', 'model': 'XGBoost', 'fold': 1, 'lr': 0.1}
    params2 = {'dataset': 'Alpha', 'model': 'XGBoost', 'fold': 2, 'lr': 0.1}
    params3 = {'dataset': 'Alpha', 'model': 'XGBoost', 'fold': 1, 'lr': 0.05}
    params4 = {'dataset': 'Alpha', 'model': 'LightGBM', 'fold': 1, 'lr': 0.1}
    params5 = {'dataset': 'Beta', 'model': 'XGBoost', 'fold': 1, 'lr': 0.1, 'extra': True}
    params6 = {'dataset': 'Gamma', 'model': 'NN', 'version': 'v2', 'lr': 0.01}
    dummy_plot = {'data': '...'}
    return {
        key_generator(params1, preserve_types=True): dummy_plot,
        key_generator(params2, preserve_types=True): dummy_plot,
        key_generator(params3, preserve_types=True): dummy_plot,
        key_generator(params4, preserve_types=True): dummy_plot,
        key_generator(params5, preserve_types=True): dummy_plot,
        key_generator(params6, preserve_types=True): dummy_plot,
    }

@pytest.fixture
def sample_plot_data_string_types():
    """Sample dict_of_all_plots with stringified types."""
    params1 = {'dataset': 'Alpha', 'model': 'XGBoost', 'fold': '1', 'lr': '0.1'}
    params2 = {'dataset': 'Alpha', 'model': 'XGBoost', 'fold': '2', 'lr': '0.1'}
    params3 = {'dataset': 'Beta', 'model': 'NN', 'fold': '1', 'lr': '0.05'}
    dummy_plot = {'data': '...'}
    return {
        key_generator(params1, preserve_types=False): dummy_plot,
        key_generator(params2, preserve_types=False): dummy_plot,
        key_generator(params3, preserve_types=False): dummy_plot,
    }

# --- Tests for get_hierarchical_parameter_options ---

def test_hierarchical_empty_dict(sample_plot_data_preserved_types):
    assert get_hierarchical_parameter_options({}, ['dataset', 'model']) == {}

def test_hierarchical_empty_key_order(sample_plot_data_preserved_types):
    assert get_hierarchical_parameter_options(sample_plot_data_preserved_types, []) == {}

def test_hierarchical_basic_preserved_types(sample_plot_data_preserved_types):
    key_order = ['dataset', 'model']
    expected = {
        'Alpha': {
            'XGBoost': {},
            'LightGBM': {}
        },
        'Beta': {
            'XGBoost': {}
        },
        'Gamma': {
            'NN': {}
        }
    }
    assert get_hierarchical_parameter_options(sample_plot_data_preserved_types, key_order, preserved_types_in_keys=True) == expected

def test_hierarchical_deeper_preserved_types(sample_plot_data_preserved_types):
    key_order = ['dataset', 'model', 'lr']
    expected = {
        'Alpha': {
            'XGBoost': {
                0.05: {},
                0.1: {}
            },
            'LightGBM': {
                0.1: {}
            }
        },
        'Beta': {
            'XGBoost': {
                0.1: {}
            }
        },
        'Gamma': {
            'NN': {
                0.01: {}
            }
        }
    }
    result = get_hierarchical_parameter_options(sample_plot_data_preserved_types, key_order, preserved_types_in_keys=True)
    assert result == expected

def test_hierarchical_string_types(sample_plot_data_string_types):
    key_order = ['dataset', 'model', 'fold']
    expected = {
        'Alpha': {
            'XGBoost': {
                '1': {},
                '2': {}
            }
        },
        'Beta': {
            'NN': {
                '1': {}
            }
        }
    }
    assert get_hierarchical_parameter_options(sample_plot_data_string_types, key_order, preserved_types_in_keys=False) == expected

def test_hierarchical_param_not_always_present(sample_plot_data_preserved_types):
    key_order = ['dataset', 'version'] # 'version' only in Gamma
    expected = {
        'Alpha': {}, # No 'version' for Alpha, so it stops
        'Beta': {},  # No 'version' for Beta
        'Gamma': {
            'v2': {}
        }
    }
    result = get_hierarchical_parameter_options(sample_plot_data_preserved_types, key_order, preserved_types_in_keys=True)
    assert result == expected
    
def test_hierarchical_malformed_key_skipped(sample_plot_data_preserved_types):
    data_with_malformed = sample_plot_data_preserved_types.copy()
    data_with_malformed["malformedkey="] = {"data": "bad"} # Add a malformed key
    key_order = ['dataset', 'model']
    expected = { # Should be same as basic test, malformed key ignored
        'Alpha': {
            'XGBoost': {},
            'LightGBM': {}
        },
        'Beta': {
            'XGBoost': {}
        },
        'Gamma': {
            'NN': {}
        }
    }
    # The reverse_key_generator in the prompt's code raises ValueError for malformed keys,
    # and get_hierarchical_parameter_options catches it and continues.
    assert get_hierarchical_parameter_options(data_with_malformed, key_order, preserved_types_in_keys=True) == expected


# --- Tests for get_all_distinct_parameter_values ---

def test_distinct_empty_dict():
    assert get_all_distinct_parameter_values({}, ['dataset', 'model']) == {'dataset': [], 'model': []}

def test_distinct_empty_param_list(sample_plot_data_preserved_types):
    assert get_all_distinct_parameter_values(sample_plot_data_preserved_types, []) == {}

def test_distinct_basic_preserved_types(sample_plot_data_preserved_types):
    params_of_interest = ['dataset', 'model', 'lr', 'extra']
    expected = {
        'dataset': ['Alpha', 'Beta', 'Gamma'],
        'model': ['LightGBM', 'NN', 'XGBoost'], # Sorted
        'lr': [0.01, 0.05, 0.1], # Sorted
        'extra': [True] # Only one entry has 'extra'
    }
    result = get_all_distinct_parameter_values(sample_plot_data_preserved_types, params_of_interest, preserved_types_in_keys=True)
    assert result == expected

def test_distinct_string_types(sample_plot_data_string_types):
    params_of_interest = ['dataset', 'fold', 'lr']
    expected = {
        'dataset': ['Alpha', 'Beta'],
        'fold': ['1', '2'], # Sorted as strings
        'lr': ['0.05', '0.1'] # Sorted as strings
    }
    assert get_all_distinct_parameter_values(sample_plot_data_string_types, params_of_interest, preserved_types_in_keys=False) == expected

def test_distinct_param_not_found(sample_plot_data_preserved_types):
    params_of_interest = ['dataset', 'non_existent_param']
    expected = {
        'dataset': ['Alpha', 'Beta', 'Gamma'],
        'non_existent_param': []
    }
    assert get_all_distinct_parameter_values(sample_plot_data_preserved_types, params_of_interest, preserved_types_in_keys=True) == expected

def test_distinct_malformed_key_skipped(sample_plot_data_preserved_types):
    data_with_malformed = sample_plot_data_preserved_types.copy()
    data_with_malformed["anothermalformed&key"] = {"data": "bad"} # Add a malformed key
    params_of_interest = ['dataset', 'model']
    expected = { # Should be same as basic test, malformed key ignored
        'dataset': ['Alpha', 'Beta', 'Gamma'],
        'model': ['LightGBM', 'NN', 'XGBoost']
    }
    # The reverse_key_generator in the prompt's code raises ValueError for malformed keys,
    # and get_all_distinct_parameter_values catches it and continues.
    assert get_all_distinct_parameter_values(data_with_malformed, params_of_interest, preserved_types_in_keys=True) == expected

# def test_distinct_mixed_types_sorting():
#     # Test sorting when values are of mixed types (should sort by string representation)
#     # This scenario is handled by the try-except block in the sorting part of the functions
#     params_mixed = {
#         'mixed_param': [10, 'apple', True, 2.5, None, {'a':1}, [1,2]]
#     }
#     dict_mixed = {key_generator(params_mixed, preserve_types=True): {}}
    
#     # For get_hierarchical_parameter_options
#     hierarchical_result = get_hierarchical_parameter_options(dict_mixed, ['mixed_param'])
#     # Expected order after sorting by string representation:
#     # repr(None) -> 'None'
#     # repr(True) -> 'True'
#     # repr(2.5) -> '2.5'
#     # repr(10) -> '10'
#     # repr('apple') -> "'apple'"
#     # repr([1,2]) -> '[1, 2]'
#     # repr({'a':1}) -> "{'a': 1}"
#     # The actual order depends on string comparison of these repr() values
    
#     # We can check if all items are present and the structure is correct.
#     # The exact sort order of complex types can be tricky, but let's ensure they are present.
#     expected_keys_hierarchical = sorted([None, True, 2.5, 10, 'apple', [1,2], {'a':1}], key=str)
#     assert sorted(list(hierarchical_result.keys()), key=str) == expected_keys_hierarchical
#     for k in expected_keys_hierarchical:
#         assert hierarchical_result[k] == {}


#     # For get_all_distinct_parameter_values
#     distinct_result = get_all_distinct_parameter_values(dict_mixed, ['mixed_param'])
#     expected_values_distinct = sorted([None, True, 2.5, 10, 'apple', [1,2], {'a':1}], key=str)
#     assert distinct_result['mixed_param'] == expected_values_distinct
