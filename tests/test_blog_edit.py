import unittest
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User
from app.models.blog import BlogPost


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestBlogEdit(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class=TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create User 1 (Author)
            self.user1 = User(
                username="alice",
                email="alice@example.com",
                password_hash=generate_password_hash("password123"),
            )
            db.session.add(self.user1)

            # Create User 2 (Other user)
            self.user2 = User(
                username="bob",
                email="bob@example.com",
                password_hash=generate_password_hash("password123"),
            )
            db.session.add(self.user2)

            db.session.commit()

            # Create a Blog Post by User 1
            self.post = BlogPost(
                title="Original Title",
                short_description="Original Short Description",
                description="Original Full Description",
                visibility="public",
                created_by_id=self.user1.id,
            )
            db.session.add(self.post)
            db.session.commit()
            self.post_id = self.post.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_unauthenticated_user_redirected_to_login(self):
        response = self.client.get(f"/blog/{self.post_id}/edit")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_author_can_access_edit_page(self):
        # Log in as user1 (author)
        login_res = self.client.post("/login", data={"username": "alice", "password": "password123"}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        response = self.client.get(f"/blog/{self.post_id}/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Original Title", response.data)
        self.assertIn(b"Original Short Description", response.data)

    def test_non_author_cannot_access_edit_page(self):
        # Log in as user2 (not author)
        login_res = self.client.post("/login", data={"username": "bob", "password": "password123"}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        response = self.client.get(f"/blog/{self.post_id}/edit", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You are not authorized to edit this post", response.data)

    def test_author_can_update_post(self):
        # Log in as user1 (author)
        self.client.post("/login", data={"username": "alice", "password": "password123"}, follow_redirects=True)
        response = self.client.post(
            f"/blog/{self.post_id}/edit",
            data={
                "title": "Updated Title",
                "short_description": "Updated Short Description",
                "description": "Updated Full Description with new details.",
                "visibility": "private",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            updated = db.session.get(BlogPost, self.post_id)
            self.assertEqual(updated.title, "Updated Title")
            self.assertEqual(updated.short_description, "Updated Short Description")
            self.assertEqual(updated.description, "Updated Full Description with new details.")
            self.assertEqual(updated.visibility, "private")

    def test_author_can_save_post_without_replacing_photo(self):
        # Set post photo path
        with self.app.app_context():
            p = db.session.get(BlogPost, self.post_id)
            p.photo = "uploads/blog/sample_image.jpg"
            db.session.commit()

        # Log in as user1 (author)
        self.client.post("/login", data={"username": "alice", "password": "password123"}, follow_redirects=True)
        response = self.client.post(
            f"/blog/{self.post_id}/edit",
            data={
                "title": "Preserved Photo Title",
                "short_description": "Preserved Photo Short",
                "description": "Preserved Photo Description",
                "visibility": "public",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            updated = db.session.get(BlogPost, self.post_id)
            self.assertEqual(updated.title, "Preserved Photo Title")
            self.assertEqual(updated.photo, "uploads/blog/sample_image.jpg")

    def test_author_can_regenerate_post(self):
        # Log in as user1 (author)
        self.client.post("/login", data={"username": "alice", "password": "password123"}, follow_redirects=True)

        from io import BytesIO
        from PIL import Image
        img_io = BytesIO()
        Image.new("RGB", (60, 60), color=(100, 150, 200)).save(img_io, format="JPEG")
        img_io.seek(0)

        response = self.client.post(
            f"/blog/{self.post_id}/regenerate",
            data={"photo": (img_io, "test.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("title", data)
        self.assertIn("short_description", data)
        self.assertIn("description", data)
        self.assertIn("copyright_check", data)

    def test_non_author_cannot_regenerate_post(self):
        # Log in as user2 (not author)
        self.client.post("/login", data={"username": "bob", "password": "password123"}, follow_redirects=True)

        from io import BytesIO
        from PIL import Image
        img_io = BytesIO()
        Image.new("RGB", (60, 60), color=(100, 150, 200)).save(img_io, format="JPEG")
        img_io.seek(0)

        response = self.client.post(
            f"/blog/{self.post_id}/regenerate",
            data={"photo": (img_io, "test.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_regenerate_post(self):
        response = self.client.post(f"/blog/{self.post_id}/regenerate")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])


if __name__ == "__main__":
    unittest.main()

