import json,tempfile,unittest
from pathlib import Path
from workspaces.sarah.codex_mediated_tools.collector import cli_command,clean_environment,create_run,assert_integrity,source_hashes

class CollectorTests(unittest.TestCase):
    def test_environment_has_no_platform_keys_or_base_url_or_inherited_home(self):
        env=clean_environment({'PATH':'/usr/bin','HOME':'/Users/example','OPENAI_API_KEY':'secret','CODEX_API_KEY':'secret','OPENAI_BASE_URL':'bad','CODEX_ACCESS_TOKEN':'secret','CODEX_HOME':'other','SHELL':'/bin/zsh'},Path('/private/tmp/newhome'))
        self.assertEqual(env['CODEX_HOME'],'/private/tmp/newhome')
        self.assertFalse(any(k in env for k in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_BASE_URL','CODEX_ACCESS_TOKEN')))

    def test_cli_command_forces_chatgpt_model_and_disables_native_shell_and_apps(self):
        args=cli_command('/bin/codex',Path('/private/tmp/empty'))
        self.assertIn('forced_login_method="chatgpt"',args)
        self.assertIn('gpt-6-sol',args);self.assertIn('--ephemeral',args)
        self.assertIn('features.shell_tool=false',args);self.assertIn('features.apps=false',args)
        self.assertNotIn('resume',args);self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',args)

    def test_exclusive_slot_and_source_change_stop_before_collection(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'run'
            create_run(p,{'a':'b'})
            with self.assertRaises(FileExistsError):create_run(p,{'a':'b'})
            with self.assertRaises(ValueError):assert_integrity({'source_sha256':{'not_a_source':'bad'}})

if __name__=='__main__':unittest.main()
