import tempfile,unittest,subprocess,sys
from pathlib import Path
from workspaces.sarah.codex_mediated_tools.isolation import seatbelt_profile,probe

class IsolationTests(unittest.TestCase):
    def test_real_os_blocks_protected_alias_and_write_with_public_read_control(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);secret=root/'protected';secret.mkdir();(secret/'data.txt').write_text('secret')
            alias=root/'alias';alias.symlink_to(secret,target_is_directory=True)
            public=root/'public.txt';public.write_text('public')
            result=probe(seatbelt_profile([secret]),secret/'data.txt',alias/'data.txt',public)
            self.assertEqual(result,{'public_read':True,'protected_read_denied':True,'alias_read_denied':True,'protected_write_denied':True})
            self.assertEqual((secret/'data.txt').read_text(),'secret')

if __name__=='__main__':unittest.main()
