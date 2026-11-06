from unittest.mock import Mock, patch

from lib.onnx import OnnxNet


def _meta_file(tmp_path):
    meta_path = tmp_path / 'model.meta'
    meta_path.write_text('names = names.txt\n')
    return str(meta_path)


def test_openvino_gpu_provider_is_configured(tmp_path, monkeypatch):
    session = Mock()
    session.get_providers.return_value = [
        'OpenVINOExecutionProvider',
        'CPUExecutionProvider',
    ]
    monkeypatch.setenv('ML_API_GPU_PROVIDER', 'OpenVINOExecutionProvider')
    monkeypatch.setenv('ML_API_OPENVINO_DEVICE', 'GPU.1')

    with patch('lib.onnx.onnxruntime.InferenceSession', return_value=session) as create_session:
        OnnxNet('model.onnx', _meta_file(tmp_path), use_gpu=True)

    assert create_session.call_args.kwargs['providers'] == [
        'OpenVINOExecutionProvider',
        'CPUExecutionProvider',
    ]
    assert create_session.call_args.kwargs['provider_options'] == [
        {'device_type': 'GPU.1'},
        {},
    ]


def test_gpu_provider_must_remain_active(tmp_path, monkeypatch):
    session = Mock()
    session.get_providers.return_value = ['CPUExecutionProvider']
    monkeypatch.setenv('ML_API_GPU_PROVIDER', 'OpenVINOExecutionProvider')

    with patch('lib.onnx.onnxruntime.InferenceSession', return_value=session):
        try:
            OnnxNet('model.onnx', _meta_file(tmp_path), use_gpu=True)
        except RuntimeError as error:
            assert 'OpenVINOExecutionProvider was requested but is not active' in str(error)
        else:
            raise AssertionError('a GPU request must not silently become CPU inference')
