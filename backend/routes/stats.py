"""
Statistics routes for MCQ Extractor AI
Handles view counts, likes, and dislikes
"""
import json
import os
from flask import Blueprint, jsonify, request
from pathlib import Path

# Create Blueprint
bp = Blueprint('stats', __name__)

# Path to stats file
STATS_FILE = Path(__file__).resolve().parent.parent.parent / 'storage' / 'stats.json'


def load_stats():
    """Load stats from JSON file"""
    try:
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    # Default stats
    return {
        "views": 100,
        "likes": 20,
        "dislikes": 0
    }


def save_stats(stats):
    """Save stats to JSON file"""
    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
        return True
    except Exception:
        return False


@bp.route('', methods=['GET'])
def get_stats():
    """Get current statistics"""
    stats = load_stats()
    return jsonify(stats), 200


@bp.route('/like', methods=['POST'])
def like():
    """Increment likes counter"""
    stats = load_stats()
    stats['likes'] = stats.get('likes', 0) + 1
    save_stats(stats)
    return jsonify({
        "success": True,
        "likes": stats['likes']
    }), 200


@bp.route('/dislike', methods=['POST'])
def dislike():
    """Increment dislikes counter"""
    stats = load_stats()
    stats['dislikes'] = stats.get('dislikes', 0) + 1
    save_stats(stats)
    return jsonify({
        "success": True,
        "dislikes": stats['dislikes']
    }), 200


@bp.route('/view', methods=['POST'])
def add_view():
    """Increment views counter"""
    return increment_view()


def increment_view():
    """Increment views counter - can be called from other modules"""
    try:
        stats = load_stats()
        stats['views'] = stats.get('views', 0) + 1
        save_stats(stats)
        return {
            "success": True,
            "views": stats['views']
        }
    except Exception:
        return {
            "success": False,
            "views": 0
        }
