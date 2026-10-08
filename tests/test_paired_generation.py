import importlib.util
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pathlib import Path
REPO = str(Path(__file__).resolve().parents[1])
spec = importlib.util.spec_from_file_location('paired_app', REPO + '/app.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PairedGenerationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_ledger = module.LEDGER
        module.LEDGER = self.tmp.name + '/allowance.sqlite3'
        self.env = patch.dict(os.environ, {'OPENAI_API_KEY': 'test-placeholder-not-a-key'})
        self.env.start()
        module.app.config.update(TESTING=True)
        self.browser = module.app.test_client()
        with self.browser.session_transaction() as session:
            session['csrf'] = 'test-csrf'
        self.provider = MagicMock()
        self.provider.responses.create.return_value = SimpleNamespace(output_text='The room remembers the sea.', status='completed')
        self.provider.images.generate.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json='mock-image-base64')])
        self.factory_patch = patch.object(module, 'OpenAI', return_value=self.provider)
        self.factory = self.factory_patch.start()
        self.form = dict(csrf='test-csrf', action='paired', prompt='An empty room remembering the sea', instructions='Be concise.', model='gpt-4.1-mini', temperature='1.2', max_tokens='150', style='early_ai')

    def tearDown(self):
        self.factory_patch.stop()
        self.env.stop()
        module.LEDGER = self.old_ledger
        self.tmp.cleanup()

    def post(self, **changes):
        return self.browser.post('/', data={**self.form, **changes}, headers={'Accept': 'application/json'})

    def test_pair_uses_same_prompt_and_companion_text(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body, dict(result='The room remembers the sea.', image='mock-image-base64', error=None, remaining=4))
        self.factory.assert_called_once_with(timeout=110, max_retries=0)
        self.assertEqual(self.provider.responses.create.call_args.kwargs['input'], self.form['prompt'])
        image_args = self.provider.images.generate.call_args.kwargs
        self.assertIn(self.form['prompt'], image_args['prompt'])
        self.assertIn(body['result'], image_args['prompt'])
        self.assertIn(module.STYLES['early_ai'], image_args['prompt'])
        self.assertEqual((image_args['model'], image_args['quality'], image_args['size'], image_args['n']), ('gpt-image-1-mini', 'low', '1024x1024', 1))

    def test_missing_action_defaults_to_pair(self):
        form = self.form.copy()
        del form['action']
        response = self.browser.post('/', data=form, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.provider.responses.create.assert_called_once()
        self.provider.images.generate.assert_called_once()

    def test_invalid_fields_make_no_provider_calls_or_reservations(self):
        for invalid in [dict(style='unknown'), dict(temperature='nan'), dict(temperature='infinity'), dict(temperature='x'), dict(max_tokens='1.5'), dict(max_tokens='501'), dict(model='unlisted'), dict(prompt=' '), dict(prompt='a'*2001), dict(instructions='a'*2001), dict(action='unknown')]:
            with self.subTest(invalid=invalid):
                response = self.post(**invalid)
                self.assertEqual(response.status_code, 400)
                self.assertIsNone(response.get_json()['result'])
                self.assertEqual(response.get_json()['remaining'], 5)
        self.factory.assert_not_called()

    def test_invalid_csrf_makes_no_calls(self):
        self.assertEqual(self.post(csrf='bad').status_code, 400)
        self.factory.assert_not_called()

    def test_image_provider_failure_retains_text_and_sanitizes_error(self):
        self.provider.images.generate.side_effect = module.OpenAIError('private-provider-details')
        response = self.post()
        body = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body['result'], 'The room remembers the sea.')
        self.assertIsNone(body['image'])
        self.assertIn('No automatic retry', body['error'])
        self.assertNotIn('private-provider-details', body['error'])
        self.assertEqual(body['remaining'], 4)
        self.provider.images.generate.assert_called_once()

    def test_text_provider_failure_never_calls_or_reserves_image(self):
        self.provider.responses.create.side_effect = module.OpenAIError('private-provider-details')
        response = self.post()
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(response.get_json()['result'])
        self.assertEqual(response.get_json()['remaining'], 5)
        self.provider.images.generate.assert_not_called()

    def test_empty_text_never_calls_or_reserves_image(self):
        self.provider.responses.create.return_value.output_text = ''
        response = self.post()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['remaining'], 5)
        self.provider.images.generate.assert_not_called()

    def test_exhausted_allowance_retains_text_without_image_call(self):
        for _ in range(5):
            module.reserve_image()
        response = self.post()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['result'], 'The room remembers the sea.')
        self.assertEqual(response.get_json()['remaining'], 0)
        self.provider.images.generate.assert_not_called()

    def test_busy_image_retains_text_without_reservation(self):
        module.image_lock.acquire()
        try:
            response = self.post()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['result'], 'The room remembers the sea.')
            self.assertEqual(response.get_json()['remaining'], 5)
            self.provider.images.generate.assert_not_called()
        finally:
            module.image_lock.release()

    def test_legacy_text_is_still_text_only(self):
        response = self.post(action='text')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()['image'])
        self.assertEqual(response.get_json()['remaining'], 5)
        self.provider.images.generate.assert_not_called()

    def test_legacy_image_is_still_image_only(self):
        response = self.post(action='image', image_prompt='A stone', prompt='', temperature='invalid')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()['result'])
        self.provider.responses.create.assert_not_called()
        self.assertIn('A stone', self.provider.images.generate.call_args.kwargs['prompt'])

    def test_incomplete_text_marker_survives_pair(self):
        self.provider.responses.create.return_value.status = 'incomplete'
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertIn('[Stopped at the response length limit.]', response.get_json()['result'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
