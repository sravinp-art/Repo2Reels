"""Final cut: the cover as frame 0, the rendered picture after it, the mixed sound, loudness set for phones.

Loudness is measured first, then normalised in a second pass to -14 LUFS (true peak -1.5 dB), then a
limiter, so every reel plays at the same level in a feed. Output: out/<project>/<brand>-reel-<n>-<slug>.mp4
plus a JPG cover next to it.

    python3 -m r2r.encode projects/keyva [r11 ...]
"""
import json
import re
import subprocess
import sys

from .common import FPS, load_project, out_name, reel_ids


def loudness_args(wav):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', str(wav), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    return (f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")


def measure(path):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr); p = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture_output=True, text=True).stdout.strip()
    return float(d), float(i[-1]), float(p[-1])


def run(project_dir, reels=None):
    proj, pdir, build, out = load_project(project_dir)
    out.mkdir(parents=True, exist_ok=True)
    for rid in reel_ids(proj, reels):
        wav, pic, poster = build / 'audio' / f'{rid}.wav', build / 'pic' / f'{rid}.mp4', build / 'posters' / f'{rid}.png'
        dst = out / (out_name(proj, rid) + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(FPS), '-t', f'{1 / FPS + .0001:.4f}', '-i', str(poster),
                        '-i', str(pic), '-i', str(wav), '-filter_complex',
                        '[0:v]trim=end_frame=1,setpts=PTS-STARTPTS,format=yuv420p[p];[1:v]trim=start_frame=1,setpts=PTS-STARTPTS[r];'
                        '[p][r]concat=n=2:v=1:a=0,format=yuv420p[v]',
                        '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-r', str(FPS),
                        '-c:a', 'aac', '-b:a', '192k', '-af', f'loudnorm=I=-14:TP=-1.5:LRA=11:{loudness_args(wav)}:linear=true,alimiter=limit=0.76:level=false,aresample=48000',
                        '-movflags', '+faststart', '-shortest', str(dst)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(poster), '-q:v', '2', str(dst.with_suffix('.jpg'))], check=True)
        d, i, p = measure(dst)
        print(f'  {dst.name}: {d:.2f}s, {i:.1f} LUFS, peak {p:.1f} dBFS')


if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], a[1:] or None)
