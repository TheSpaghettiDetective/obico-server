import glob
import os.path
import pytest

def test_health_check(client):
    response = client.get("/hc/")
    assert b"ok" in response.data

fail_imgs = glob.glob('./tests/failure/*.png')
nofail_imgs = glob.glob('./tests/nofailure/*.png')
@pytest.mark.parametrize("impath,expect_fail", [(p,True) for p in fail_imgs] + [(p, False) for p in nofail_imgs])
def test_detect_spaghetti(client, requests_mock, impath, expect_fail):
    with open(impath, 'rb') as f:
        data = f.read()
    imurl = 'http://testimgsrv.com/' + os.path.basename(impath)
    requests_mock.get(imurl, content=data)

    response = client.get("/p/?img=" + imurl)
    if expect_fail:
        assert len(response.json.get('detections', [])) > 0
    else:
        assert len(response.json.get('detections', [])) == 0

