# Video2Video
[FFMPeg](https://www.ffmpeg.org/)과 [FFMPeg-Python](https://github.com/kkroening/ffmpeg-python)를 사용하여 Video to Video 변환을 수행하는 Python Package 입니다. 

비디오 변환 시, 각 Frame에 추가적인 처리를 편하게 하기 위해 제작되었습니다.

## Main Status

[![Unit Tests](https://github.com/404Vector/Video2Video/actions/workflows/unit_test.yml/badge.svg?branch=main)](https://github.com/404Vector/Video2Video/actions/workflows/unit_test.yml)
[![Check Format](https://github.com/404Vector/Video2Video/actions/workflows/black-formatter-action.yml/badge.svg?branch=main)](https://github.com/404Vector/Video2Video/actions/workflows/black-formatter-action.yml)
[![Publish to PyPi](https://github.com/404Vector/Video2Video/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/404Vector/Video2Video/actions/workflows/pypi-publish.yml)


## Install

```bash
pip install v2v
```
- PyPi URL : https://pypi.org/project/v2v/

## Example

### Video2ImageProcessor

비디오에서 이미지들을 추출합니다. ([Example](https://github.com/404Vector/Video2Video/blob/main/tests/_test_v2i_.py))

### Image2VideoProcessor

이미지들을 사용하여 비디오를 생성합니다. ([Example](https://github.com/404Vector/Video2Video/blob/main/tests/_test_i2v_.py))

### AudioExtractor

비디오에서 오디오를 추출합니다. ([Example](https://github.com/404Vector/Video2Video/blob/main/tests/_test_v2a_.py))

### AudioMerger

비디오와 오디오를 병합하여 새롭게 비디오를 생성합니다. ([Example](https://github.com/404Vector/Video2Video/blob/main/tests/_test_v2i2v_.py))

### Video2VideoProcessor

위 클래스들을 활용하여 비디오를 비디오로 변환합니다. ([Example](https://github.com/404Vector/Video2Video/blob/main/tests/_test_v2v_.py))


## Use Video2VideoProcessor
Video2VideoProcessor는 Constructor method의 Parameter로 'frame_processor_pool'을 받습니다.
- frame_processor_pool | type : IFrameProcessorPool  

이 Instance(frame_processor_pool)는 내부적으로 frame이 생성 될 때 마다 호출됩니다. 

따라서 Abstracted Class인 IFrameProcessorPool을 상속하여 새로운 Class를 생성한 뒤,  
그 Class의 Instance를 frame_processor_pool 파라미터로 넘겨주면 Frame 별 Processing이 가능합니다.

IFrameProcessorPool을 상속한 Class의 생성은 [이 코드](https://github.com/404Vector/Video2Video/blob/main/v2v/_null_frame_processor_pool_.py)와 [이 코드](https://github.com/404Vector/Video2Video/blob/main/v2v/_null_frame_processor_.py)를 참조하세요.
