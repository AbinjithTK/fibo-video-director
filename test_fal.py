import fal_client
import os

os.environ['FAL_KEY'] = '0686f907-db80-4f72-9cc8-50cd387df550:f5efdaf22a5ea55d5bb28d42da165cbd'

result = fal_client.subscribe(
    'bria/fibo/generate',
    arguments={
        'prompt': 'A majestic elephant walking through African savanna at sunset',
        'seed': 42,
        'aspect_ratio': '16:9'
    }
)
print('Success!')
print(f"Image URL: {result['image']['url']}")
