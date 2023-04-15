from datetime import datetime, timedelta, timezone
class ShowActivities:
  def run(activity_uuid):
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': 'eced682e-7c25-41fc-affb-461028921fdd',
      'handle':  'rhys',
      'message': 'Cloud is fun!',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'replies': {
        'uuid': 'cbf319a7-7f65-4012-823c-b3fc7d2ec9d8',
        'handle':  'tate',
        'message': 'This post has no honor!',
        'created_at': (now - timedelta(days=2)).isoformat()
      }
    }]
    return results