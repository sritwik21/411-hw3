#Comment: Copy of playlist_model
import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    #Comment: 'battle_model' or 'kitchen_model'?
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 1, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 10, 'HIGH')

@pytest.fixture
def sample_meal3():
    return Meal(3, 'Meal 3', 'Cuisine 3', 5, 'MED')

@pytest.fixture
#Change 1: 'sample_playlist' --> 'sample_battle'; Comment: 'sample_battle' or 'sample_combatant_list'
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Add Meal Management Test Cases
##################################################
#Comment: Need to create unit test for battle function
def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a meal to the list."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_prep_combatant_duplicate(battle_model, sample_meal1):
    """Test error when adding a duplicate meal to the list."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Meal with ID 1 already exists in the list"):
        battle_model.prep_combatant(sample_meal1)

def test_prep_combatant_full(battle_model, sample_meal3):
    """Test error when adding a meal to the full list."""
    battle_model.combatants.extend(sample_battle)
    with pytest.raises(ValueError, match="Combatants list is full"):
        battle_model.prep_combatant(sample_meal3)

##################################################
# Remove Meal Management Test Cases
##################################################
def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing the entire list."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "List should be empty after clearing"

#Comment: Unit test might not be needed b/c no edge case in code (i.e. 'clear_combatants' function does not check for empty list)
def test_clear_combatants_empty_list(battle_model, caplog):
    """Test clearing the entire list when it's empty."""
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "List should be empty after clearing"
    assert "Clearing an empty list" in caplog.text, "Expected warning message when clearing an empty list"

##################################################
# Battle Management Test Cases
##################################################
def test_battle(battle_model, sample_battle):
    '''Test successfully conducting a battle between two meals'''
    battle_model.combatants.extend(sample_battle)
    try:
        winner = battle_model.battle()
        
        assert winner == "Meal 1" or "Meal 2", f"Expected either Meal 1 or Meal 2, but got {winner}"
        #Comment: Don't need to check if battle stats are correctly updated --> unit tests for 'update_meal_stats' has this covered
        assert len(battle_model.combatants) == 1, f"Expected length of combatants list to decrease (i.e. loser was removed), but length = {len(battle_model.combatants)}"

    except Exception:
        pytest.fail("battle function raised unexpected error")

def test_battle_insufficient(battle_model):
    '''Test error from conducting a battle with less than 2 combatants (i.e. one combatant)'''
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Not enough combatants"):
        battle_model.battle()
##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test successfully retrieving a combatant's battle score by its attributes."""
    battle_model.prep_combatant(sample_meal1)

    score = battle_model.get_battle_score(sample_meal1)
    difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
    assert score == (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]    

def test_get_battle_score_empty_list(battle_model, sample_meal1):
    """Test successfully retrieving a combatant's battle score by its attributes despite empty list."""
    battle_model.clear_combatants()
    try:
        score = battle_model.get_battle_score(sample_meal1)
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
        assert score == (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]
    except Exception:
        pytest.fail("get_battle_score function raised unexpected error with empty combatants list")

#Comment: Unit test might be unnecessary --> Already covered by 'test_get_battle_score'
def test_get_battle_score_full_list(battle_model, sample_battle, sample_meal1):
    """Test successfully retrieving a combatant's battle score by its attributes despite full list."""
    battle_model.combatants.extend(sample_battle)
    try:
        score = battle_model.get_battle_score(sample_meal1)
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
        assert score == (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]
    except Exception:
        pytest.fail("get_battle_score function raised unexpected error with full combatants list")

#Comment: Unit test might be uncessary --> Already covered by 'test_get_battle_score_empty_list'
def test_get_battle_score_unrelated_meal(battle_model, sample_battle, sample_meal3):
    """Test successfully retrieving a combatant's battle score by its attributes despite not being in combatants list."""
    battle_model.combatants.extend(sample_battle)
    try:
        score = battle_model.get_battle_score(sample_meal3)
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
        assert score == (sample_meal3.price * len(sample_meal3.cuisine)) - difficulty_modifier[sample_meal3.difficulty]
    except Exception:
        pytest.fail("get_battle_score function raised unexpected error with unrelated meal")


def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all combatants from the list."""
    battle_model.combatants.extend(sample_battle)

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_get_combatants_empty_list(battle_model):
    """Test successfully retrieving all combatants from the empty list."""
    battle_model.clear_combatants()

    empty_list = battle_model.get_combatants()
    assert len(empty_list) == 0

