import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing_utils import TextEntry, process_csv_bytes, group_horizontally, group_vertically, build_grouping_result


class TestProcessingUtils:
    """Test cases for CSV processing and grouping logic"""
    
    def test_process_csv_valid_data(self):
        csv_data = b"text,x,y\nHello,10,10\nWorld,12,10\nThis,50,20"
        entries = process_csv_bytes(csv_data)
        
        assert len(entries) == 3
        
        assert entries[0].text == "Hello"
        assert entries[0].x == 10.0
        assert entries[0].y == 10.0
        
        assert entries[1].text == "World"
        assert entries[2].text == "This"

    def test_group_horizontally_groups(self):
        entries = [
            TextEntry("Hello", 10, 10),
            TextEntry("World", 12, 10),
            TextEntry("This", 50, 20),
            TextEntry("Is", 52, 20),
        ]
        
        groups = group_horizontally(entries)
        
        assert len(groups) == 2
        
        group_10 = next(g for g in groups if g["y"] == 10)
        assert set(group_10["texts"]) == {"Hello", "World"}
        
        group_20 = next(g for g in groups if g["y"] == 20)
        assert set(group_20["texts"]) == {"This", "Is"}

    def test_build_grouping_result_flow(self):
        entries = [
            TextEntry("Hello", 10, 10),
            TextEntry("World", 12, 10),
            TextEntry("This", 50, 20),
            TextEntry("Is", 52, 20),
            TextEntry("Test", 55, 20),
        ]
        
        result = build_grouping_result(entries)
        
        assert "horizontal_groups" in result
        assert "vertical_groups" in result
        
        assert len(result["horizontal_groups"]) == 2
        
        assert len(result["vertical_groups"]) == 5
        
        horizontal_ys = {g["y"] for g in result["horizontal_groups"]}
        assert horizontal_ys == {10, 20}
        
        vertical_xs = {g["x"] for g in result["vertical_groups"]}
        assert vertical_xs == {10, 12, 50, 52, 55}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])