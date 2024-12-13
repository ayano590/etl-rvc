import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from infer.modules.vc.modules import VC
import torch
import fairseq
import warnings
import shutil
import logging
from scipy.io.wavfile import write
from configs.config import (Config,
                            spk_item,
                            vc_transform0,
                            f0_file,
                            f0method0,
                            index_rate1,
                            filter_radius0,
                            resample_sr0,
                            rms_mix_rate0,
                            protect0,
                            male_streamer,
                            male_voice)

from staging import extract_wav


logging.getLogger("numba").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

tmp = os.path.join(now_dir, "TEMP")
shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree("%s/runtime/Lib/site-packages/infer_pack" % (now_dir), ignore_errors=True)
os.makedirs(tmp, exist_ok=True)
os.makedirs(os.path.join(now_dir, "logs"), exist_ok=True)
os.makedirs(os.path.join(now_dir, "assets/weights"), exist_ok=True)
os.environ["TEMP"] = tmp
warnings.filterwarnings("ignore")
torch.manual_seed(114514)

config = Config()
vc = VC(config)

if config.dml == True:

    def forward_dml(ctx, x, scale):
        ctx.scale = scale
        res = x.clone().detach()
        return res

    fairseq.modules.grad_multiply.GradMultiply.forward = forward_dml

# check if a CUDA compatible GPU is available
ngpu = torch.cuda.device_count()
gpu_infos = []
mem = []
if_gpu_ok = False

if torch.cuda.is_available() or ngpu != 0:
    for i in range(ngpu):
        gpu_name = torch.cuda.get_device_name(i)
        if any(
            value in gpu_name.upper()
            for value in [
                "10",
                "16",
                "20",
                "30",
                "40",
                "A2",
                "A3",
                "A4",
                "P4",
                "A50",
                "500",
                "A60",
                "70",
                "80",
                "90",
                "M4",
                "T4",
                "TITAN",
            ]
        ):
            # A10#A100#V100#A40#P40#M40#K80#A4500
            if_gpu_ok = True  # at least one compatible GPU found
            gpu_infos.append("%s\t%s" % (i, gpu_name))
            mem.append(
                int(
                    torch.cuda.get_device_properties(i).total_memory
                    / 1024
                    / 1024
                    / 1024
                    + 0.4
                )
            )
if if_gpu_ok and len(gpu_infos) > 0:
    gpu_info = "\n".join(gpu_infos)
    default_batch_size = min(mem) // 2
else:
    gpu_info = "No compatible GPU found"
    default_batch_size = 1
gpus = "-".join([i[0] for i in gpu_infos])

# load environment
weight_root = os.getenv("weight_root")
index_root = os.getenv("index_root")
lv_orig_dir = os.getenv("lv_orig_dir")
lv_conv_dir = os.getenv("lv_conv_dir")
tw_orig_wav_dir = os.getenv("tw_orig_wav_dir")
tw_orig_mp4_dir = os.getenv("tw_orig_mp4_dir")
tw_conv_wav_dir = os.getenv("tw_conv_wav_dir")
tw_conv_mp4_dir = os.getenv("tw_conv_mp4_dir")


def tw_orig_extract_wav():

    # extract audio from original twitch clips
    # access video files
    for name in os.listdir(tw_orig_mp4_dir):

        # change output file extension to .wav
        file_format = name.split(".")[-1]
        output_name = name.replace(file_format, "wav")

        if not os.path.isfile(tw_orig_wav_dir + "/audio/" + output_name):

            # extract audio and save it in specified directory
            extract_wav.extract(tw_orig_mp4_dir + "/" + name, tw_orig_wav_dir + "/audio/" + output_name)

def lv_infer():

    input_audio_dir = lv_orig_dir + "/audio"

    # infer all lv tracks with each respective model
    # iterate over inference models
    for lang in os.listdir(weight_root):

        # skip .gitignore file
        if ".gitignore" in lang:
            continue

        spk_lang = lang.split(".")[0]

        # iterate over lv tracks
        for file_name in os.listdir(input_audio_dir):
            [title, file_format] = file_name.split(".")

            # skip inference if voice is not the same
            if spk_lang != title:
                continue

            # set output path, skip inference is file already converted
            output_path = f"{lv_conv_dir}/audio/{title}.wav"

            if os.path.isfile(output_path):
                continue

            # set inference voice
            _, _, _, file_index2, _ = vc.get_vc(
                                                lang,
                                                protect0,
                                                protect0)
            
            file_index1 = index_root + "/" + spk_lang + ".index"

            # infer
            log_out, (sample_rate, audio_out) = vc.vc_single(
                                                spk_item,
                                                input_audio_dir + "/" + file_name,
                                                vc_transform0,
                                                f0_file,
                                                f0method0,
                                                file_index1,
                                                file_index2,
                                                index_rate1,
                                                filter_radius0,
                                                resample_sr0,
                                                rms_mix_rate0,
                                                protect0)
            
            print(log_out)

            write(output_path, sample_rate, audio_out)

def tw_infer():

    input_audio_dir = tw_orig_wav_dir + "/audio"

    # infer all tw clips with all trained models
    # iterate over inference models
    for lang in os.listdir(weight_root):

        # skip .gitignore file
        if ".gitignore" in lang:
            continue

        # set infer base level
        spk_lang = lang.split(".")[0]
        if spk_lang in male_voice:
            infer_voice = 0
        else:
            infer_voice = 12

        # iterate over tw clips
        for file_name in os.listdir(input_audio_dir):
            [title, file_format] = file_name.split(".")

            # set streamer base level
            if title in male_streamer:
                streamer_voice = 0
            else:
                streamer_voice = 12

            # transpose
            vc_transform0 = infer_voice - streamer_voice

            # set output path, skip inference is file already converted
            output_path = f"{tw_conv_wav_dir}/audio/{title}_{spk_lang}.wav"

            if os.path.isfile(output_path):
                continue

            # set inference voice
            _, _, _, file_index2, _ = vc.get_vc(
                                                lang,
                                                protect0,
                                                protect0)
            
            file_index1 = index_root + "/" + spk_lang + ".index"

            # infer
            log_out, (sample_rate, audio_out) = vc.vc_single(
                                                spk_item,
                                                input_audio_dir + "/" + file_name,
                                                vc_transform0,
                                                f0_file,
                                                f0method0,
                                                file_index1,
                                                file_index2,
                                                index_rate1,
                                                filter_radius0,
                                                resample_sr0,
                                                rms_mix_rate0,
                                                protect0)
            
            print(log_out)

            write(output_path, sample_rate, audio_out)


if __name__ == "__main__":
    tw_orig_extract_wav()
    lv_infer()
    tw_infer()