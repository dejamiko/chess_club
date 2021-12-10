from clubs.models import User


def _create_test_users(start_id=0, count=5):
    for user_id in range(start_id, start_id + count):
        temp_user = User.objects.create_user(
            id=user_id,
            first_name=f"First {user_id}",
            last_name=f"Last {user_id}",
            email=f"{user_id}@test.com",
            chess_exp="Beginner",
        )
        temp_user.save()
