import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()
from infer.modules.vc.modules import VC
from i18n.i18n import I18nAuto
from configs.config import Config
import torch
import fairseq
import warnings
import shutil
import logging

from scipy.io.wavfile import write
from configs.config import (lv_orig_dir,
                            lv_conv_dir,
                            tw_orig_wav_dir,
                            tw_conv_wav_dir,
                            weights_dir,
                            index_dir)


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
i18n = I18nAuto()
logger.info(i18n)
# check if the computer has a GPU compatible with CUDA
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
            if_gpu_ok = True  # at least one GPU available
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
    gpu_info = "No compatible GPU"
    default_batch_size = 1
gpus = "-".join([i[0] for i in gpu_infos])


weight_root = os.getenv("weight_root")
index_root = os.getenv("index_root")


male_streamer = ["Trymacs", "HandOfBlood"]
male_voice = ["german", "german_experimental", "spanish"]
streamer_voice = None
infer_voice = None

spk_item = 0  # ID of speaker, leave as is
input_audio0 = tw_orig_wav_dir + "\\audio"  # path to the tw original wav audio folder, adding video titles in the code
vc_transform0 = 0  # voice transpose
f0_file = None  # not sure
f0method0 = "rmvpe"  # inference method
file_index1 = None  # same as with input_audio0
file_index2 = None  # dropdown list in gradio
index_rate1 = 0.5
filter_radius0 = 3
resample_sr0 = 0
rms_mix_rate0 = 0.25
protect0 = 0.25

def tw_infer():

    # infer all tw clips with all trained models
    for file_name in os.listdir(input_audio0):
        [title, file_format] = file_name.split(".")

        # set streamer base level
        if title in male_streamer:
            streamer_voice = 0
        else:
            streamer_voice = 12

        # select language
        for lang in os.listdir(weights_dir):

            # skip .gitignore file
            if ".gitignore" in lang:
                continue

            # set infer base level
            spk_lang = lang.split(".")[0]
            if spk_lang in male_voice:
                infer_voice = 0
            else:
                infer_voice = 12

            # skip if file already exists
            output_path = f"{tw_conv_wav_dir}\\audio\\{title}_{spk_lang}.wav"

            if not os.path.isfile(output_path):
                continue

            # transpose
            vc_transform0 = infer_voice - streamer_voice

            # set inference voice
            _, _, _, file_index2, _ = vc.get_vc(
                                                            lang,
                                                            protect0,
                                                            protect0
                                                        )
            
            file_index1 = index_dir + "\\" + spk_lang + ".index"

            # infer
            log_out, (sample_rate, audio_out) = vc.vc_single(
                                                spk_item,
                                                input_audio0 + "\\" + file_name,
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
    tw_infer()