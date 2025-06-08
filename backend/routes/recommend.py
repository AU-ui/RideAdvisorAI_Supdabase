from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

# Mock user features (e.g., [likes electric, dislikes SUV, likes fast])
user_features_db = {
    "user1": np.array([1, 0, 1]),
    "user2": np.array([0, 1, 0]),
    "user3": np.array([1, 1, 1]),
}
# Mock item features (e.g., avatars/cars)
item_features = np.array([
    [1, 0, 1],  # Tesla Model 3
    [0, 1, 0],  # Toyota Highlander
    [1, 1, 1],  # Ford Mustang Mach-E
])
item_names = ["Tesla Model 3", "Toyota Highlander", "Ford Mustang Mach-E"]
item_avatars = [
    "https://api.dicebear.com/7.x/adventurer/svg?seed=tesla",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=highlander",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=mustang",
]
# Mock user-item interaction matrix
user_item_matrix = np.array([
    [1, 0, 1],  # user1's choices
    [0, 1, 0],  # user2's choices
    [1, 1, 1],  # user3's choices
])
user_ids = ["user1", "user2", "user3"]

@router.get("/car-avatar")
def recommend_car_avatar(user_id: str = Query(..., description="User ID for recommendation")):
    if user_id not in user_features_db:
        raise HTTPException(status_code=404, detail="User not found in mock DB")
    user_idx = user_ids.index(user_id)
    user_features = user_features_db[user_id].reshape(1, -1)

    # 1. Content-based score
    content_scores = cosine_similarity(user_features, item_features)[0]

    # 2. Collaborative score (user similarity)
    user_similarities = cosine_similarity(user_features, user_item_matrix)
    collab_scores = user_similarities.dot(user_item_matrix) / user_similarities.sum()

    # 3. Hybrid score (weighted sum)
    alpha = 0.5
    hybrid_scores = alpha * content_scores + (1 - alpha) * collab_scores[0]
    recommended_index = int(np.argmax(hybrid_scores))

    return {
        "car_name": item_names[recommended_index],
        "avatar_url": item_avatars[recommended_index],
        "score": float(hybrid_scores[recommended_index]),
        "method": "hybrid (content + collaborative)"
    } 