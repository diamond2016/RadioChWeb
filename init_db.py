from radioch_app import app, db
from model.entity.stream_type import StreamType

def init_db():
    with app.app_context():
        db.create_all()
        # Seed initial stream types if not exist
        if not StreamType.query.first():
            stream_types = [
                StreamType(protocol='HTTP', format='MP3', metadata_type='Shoutcast', display_name='Shoutcast MP3'),
                StreamType(protocol='HTTP', format='AAC', metadata_type='Icecast', display_name='Icecast AAC'),
                # Add more as needed
            ]
            db.session.add_all(stream_types)
            db.session.commit()
        print("Database initialized.")

if __name__ == '__main__':
    init_db()