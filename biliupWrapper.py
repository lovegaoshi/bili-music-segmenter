import re

def cell_stdout(cmd, silent = False, encoding=None):
    print('calling', cmd, 'in terminal:')
    with subprocess.Popen(cmd) as p:
        p.wait()
    return p.returncode

def bilibili_upload(globbed, media_basename, source = None, description = None, episode_limit=10):
    ripped_from = re.findall('\[.+\]', media_basename)[0][1:-1]
    if source is None:
        try:
            source = keystamps[ripped_from][0]
        except KeyError:
            raise KeyError('cant determine source url for this repost')
            source = ' '
    if description is None:
        try:
            description = keystamps[ripped_from][1]
        except:
            description = '关注{}：{}'.format(
                                           ripped_from,
                                           source,)
    try:
        tags = keystamps[ripped_from][2]
    except:
        tags = [ripped_from]
    title = media_basename[:media_basename.rfind('.')][:60]
    # title rework: [歌切][海德薇Hedvika] 20220608
    title = tags[0] + ' ' + os.path.splitext(media_basename)[0][-8:]
    globbed = sorted(globbed)
    globbed_episode_limit = []
    for i in range(len(globbed) // episode_limit + 1):
        globbed_episode_limit.append(globbed[i * episode_limit : (i + 1) * episode_limit])
    
    for i in range(len(globbed_episode_limit)):
        if i > 0: episode_limit_prefix = '_' + chr(97 + i)
        else: episode_limit_prefix = ''
        retry = 0
        cmd = [
                './biliup',
                'upload',
            ]
        for x in globbed_episode_limit[i]: cmd.append(x)
        cmd.append('--copyright=2')
        cmd.append('--desc="{}"'.format(description))
        cmd.append('--tid=31')
        cmd.append('--tag="{}"'.format(','.join(tags)))
        cmd.append('--title="[歌切]{}"'.format(media_basename[:media_basename.rfind('.')][:60] + episode_limit_prefix))
        cmd.append('--source="{}"'.format(source))
        while cell_stdout(cmd) != 0:
            retry += 1
            if retry > 10: raise Exception('biliup failed for a total of {} times'.format(str(retry)))
#=================================================================================================================    
#AIO 一键url to b站上传
#=================================================================================================================
import glob, json, os
from inaseg import ytbdl, strip_medianame_out, shazaming, put_medianame_backin
keystring = ''

keystamps = {
    '贝萨Bessa':[r'https://live.bilibili.com/22288476',
                 r'关注贝萨贝老师：https://space.bilibili.com/592726738/'],
    '海德薇的录播组':[r'https://live.bilibili.com/24088644',
                 r'关注海德薇海老师：https://space.bilibili.com/1285890335/',
               ['海德薇Hedvika']],
    '末莱Moonlight':[
        r'https://live.bilibili.com/24463489',
        '关注末莱Moonlight木老师：https://space.bilibili.com/476185026'
    ],
    '范塞尼尔录播组':[
        r'https://live.bilibili.com/24963677',
        '关注范塞尼尔_VamSenior喵，关注范塞尼尔_VamSenior谢谢喵：https://space.bilibili.com/2042629175',
        ['范塞尼尔_VamSenior']
    ],
    '盖乃希亞Galaxy':[
        r'https://live.bilibili.com/22864117',
        '关注盖乃希亞Galaxy盖老师：https://space.bilibili.com/1846208014',
    ],
    '莱妮娅_Rynia':[
        r'https://live.bilibili.com/22605289',
        '关注莱妮娅_Rynia莱老师：https://space.bilibili.com/703018634/channel/series',
    ],
}
                #https://www.bilibili.com/video/BV12v4y1M7Vy
rs = '''
https://www.bilibili.com/video/BV1VU4y1Q7pd
https://www.bilibili.com/video/BV1Ma411x7LE
https://www.bilibili.com/video/BV1Sv4y1g7Jb
https://www.bilibili.com/video/BV1ig411Q71Y
https://www.bilibili.com/video/BV1WY4y1G7Gp
https://www.bilibili.com/video/BV1WB4y1Q7wJ
https://www.bilibili.com/video/BV1BW4y1r7xf
https://www.bilibili.com/video/BV1j94y1m7SF
https://www.bilibili.com/video/BV1wW4y1C7kx
https://www.bilibili.com/video/BV1qr4y1x7sq
https://www.bilibili.com/video/BV1p3411375L
https://www.bilibili.com/video/BV1PY4y1V7Dc
https://www.bilibili.com/video/BV153411P7X5
https://www.bilibili.com/video/BV1jY4y1r7Sn
https://www.bilibili.com/video/BV11B4y1C7KP
https://www.bilibili.com/video/BV1Vu411r7qx
https://www.bilibili.com/video/BV1AY4y1Y78B
https://www.bilibili.com/video/BV1tT4y1a7zY
https://www.bilibili.com/video/BV1qa411e7v3
https://www.bilibili.com/video/BV13q4y1e7MG
https://www.bilibili.com/video/BV1bZ4y1m73V
https://www.bilibili.com/video/BV1a34y147WC
https://www.bilibili.com/video/BV1m44y1A7UX
https://www.bilibili.com/video/BV1Bu411v7Gf
https://www.bilibili.com/video/BV1vr4y1W71g
https://www.bilibili.com/video/BV1Nq4y1e793
https://www.bilibili.com/video/BV1PR4y1F7gE
https://www.bilibili.com/video/BV1U34y147WP
https://www.bilibili.com/video/BV1244y1N7SA
https://www.bilibili.com/video/BV1cT4y1S7sH
https://www.bilibili.com/video/BV1rP4y1u7H8
https://www.bilibili.com/video/BV1UL411P7bC
https://www.bilibili.com/video/BV1Ki4y1k7Wn
https://www.bilibili.com/video/BV1cP4y1u7JC
https://www.bilibili.com/video/BV1vY41137LW
https://www.bilibili.com/video/BV14b4y1s7ko
https://www.bilibili.com/video/BV1ir4y1B7PB
https://www.bilibili.com/video/BV1zu411B7ou
https://www.bilibili.com/video/BV1gP4y137Xr
https://www.bilibili.com/video/BV1xU4y1o7LG
https://www.bilibili.com/video/BV1Li4y1C7qn
https://www.bilibili.com/video/BV1Zq4y1i74Y
https://www.bilibili.com/video/BV1Gb4y1s78P
https://www.bilibili.com/video/BV1UU4y1f7u8
https://www.bilibili.com/video/BV1zL411N7Fi
https://www.bilibili.com/video/BV1744y1M7mM
https://www.bilibili.com/video/BV1yT4y1S7dG
https://www.bilibili.com/video/BV1HL411N7gf
https://www.bilibili.com/video/BV1u341157Tj
https://www.bilibili.com/video/BV1aT4y1S71n
https://www.bilibili.com/video/BV1R44y1n7fv
https://www.bilibili.com/video/BV19L411K7ui
https://www.bilibili.com/video/BV1Wi4y127G4
https://www.bilibili.com/video/BV1N34y1y7zR
https://www.bilibili.com/video/BV11P4y1F7Ln
https://www.bilibili.com/video/BV1534y1C7Bc
https://www.bilibili.com/video/BV163411776G
https://www.bilibili.com/video/BV1sT4y1X7er
https://www.bilibili.com/video/BV1KR4y1L7z9
https://www.bilibili.com/video/BV1iu41197RA
https://www.bilibili.com/video/BV1AY411L7qP
https://www.bilibili.com/video/BV1h34y117d5
https://www.bilibili.com/video/BV1WT4y1C7ap
https://www.bilibili.com/video/BV1FS4y157zT
https://www.bilibili.com/video/BV1yq4y1h71Z
https://www.bilibili.com/video/BV15b4y1E73v
https://www.bilibili.com/video/BV1AL411F7yK
https://www.bilibili.com/video/BV16P4y177P6
https://www.bilibili.com/video/BV1Qb4y1H7ax
https://www.bilibili.com/video/BV1ER4y1M7EJ
https://www.bilibili.com/video/BV1tT4y1m7hW
https://www.bilibili.com/video/BV1R44y1j7Me
https://www.bilibili.com/video/BV1Ja411z7Hm
https://www.bilibili.com/video/BV1mL411V7ye
https://www.bilibili.com/video/BV1Qm4y1S7Nb
https://www.bilibili.com/video/BV1qR4y1u71H
https://www.bilibili.com/video/BV1ji4y19775
https://www.bilibili.com/video/BV1pL4y1J7nn
https://www.bilibili.com/video/BV1fD4y1F7sy
https://www.bilibili.com/video/BV1kP4y1J7Ym
https://www.bilibili.com/video/BV17R4y137Qt
https://www.bilibili.com/video/BV1wM4y1F7eu
https://www.bilibili.com/video/BV1BL41157T6
https://www.bilibili.com/video/BV1pr4y1S7BL
https://www.bilibili.com/video/BV1sa41167GL
https://www.bilibili.com/video/BV1AS4y1M7du
https://www.bilibili.com/video/BV1Ni4y1o7BW
https://www.bilibili.com/video/BV1DZ4y1Q7dL
https://www.bilibili.com/video/BV1qM4y1c7mq
https://www.bilibili.com/video/BV11q4y1q7RE
https://www.bilibili.com/video/BV1n3411t7kk
https://www.bilibili.com/video/BV1Na411k75B
https://www.bilibili.com/video/BV1Aq4y1B72c
https://www.bilibili.com/video/BV1WR4y1x7Lh
https://www.bilibili.com/video/BV1jP4y1G7d8
https://www.bilibili.com/video/BV1GS4y1Q7Tq
https://www.bilibili.com/video/BV1wq4y1B7Na
https://www.bilibili.com/video/BV1zi4y1d7Vz
https://www.bilibili.com/video/BV1a34y1X7ER
https://www.bilibili.com/video/BV1ig411P7xN
https://www.bilibili.com/video/BV1y341147bZ
https://www.bilibili.com/video/BV1v3411475b
https://www.bilibili.com/video/BV1XZ4y1X7eH
https://www.bilibili.com/video/BV1Db4y1B7Vs
https://www.bilibili.com/video/BV1ff4y1K74c
https://www.bilibili.com/video/BV1134y1R7CV
https://www.bilibili.com/video/BV1vU4y1T7Ws
https://www.bilibili.com/video/BV1JL4y1p7Fu
https://www.bilibili.com/video/BV15q4y1g7PZ
https://www.bilibili.com/video/BV14L4y1p7fq
https://www.bilibili.com/video/BV1kL411M7aT
https://www.bilibili.com/video/BV1q3411t7sp
https://www.bilibili.com/video/BV1pY41147ST
https://www.bilibili.com/video/BV1yf4y1T7kp
https://www.bilibili.com/video/BV14q4y1k7Qp
https://www.bilibili.com/video/BV1ph411b741
https://www.bilibili.com/video/BV1mL4y1v76C
https://www.bilibili.com/video/BV1qS4y1d7bS
https://www.bilibili.com/video/BV1Zh411t71y
https://www.bilibili.com/video/BV1iU4y1g7d1
https://www.bilibili.com/video/BV1Ur4y1C7Wk
https://www.bilibili.com/video/BV1NP4y157We
https://www.bilibili.com/video/BV1WP4y1j7pH
https://www.bilibili.com/video/BV1fQ4y1q7on
https://www.bilibili.com/video/BV18F411e7mv
https://www.bilibili.com/video/BV15h41187sE
https://www.bilibili.com/video/BV1iR4y17734
https://www.bilibili.com/video/BV1fL411g7Cp
https://www.bilibili.com/video/BV1gq4y1G7Vn
https://www.bilibili.com/video/BV1jL4y1B75a
https://www.bilibili.com/video/BV1DU4y1F7WK
https://www.bilibili.com/video/BV1Df4y1g78a
https://www.bilibili.com/video/BV1Fr4y1m7Y4
https://www.bilibili.com/video/BV1nv41137Jo
https://www.bilibili.com/video/BV1xU4y1F7Fu
https://www.bilibili.com/video/BV19Q4y1B7sk
https://www.bilibili.com/video/BV1EU4y1F7zs
https://www.bilibili.com/video/BV11Q4y1X7R7
https://www.bilibili.com/video/BV1Zh411J7D8
https://www.bilibili.com/video/BV1mP4y187JV
https://www.bilibili.com/video/BV1Nq4y1d7Ky
https://www.bilibili.com/video/BV1Kf4y1c73r
https://www.bilibili.com/video/BV1Pv411G7SB
https://www.bilibili.com/video/BV1Ph411H7UW
https://www.bilibili.com/video/BV1gQ4y167ir
https://www.bilibili.com/video/BV18q4y1P7bL
https://www.bilibili.com/video/BV1244y1b7Pd
https://www.bilibili.com/video/BV1dP4y1h7x6
https://www.bilibili.com/video/BV1yg411c7K6
https://www.bilibili.com/video/BV16h411n7op
https://www.bilibili.com/video/BV1844y147vv
https://www.bilibili.com/video/BV13f4y1E7xD
https://www.bilibili.com/video/BV1eL411x7SP
https://www.bilibili.com/video/BV1sf4y1n7BN
https://www.bilibili.com/video/BV1tL4y1a7kT
https://www.bilibili.com/video/BV1kv411w7m3
https://www.bilibili.com/video/BV1Tf4y1n7oH
https://www.bilibili.com/video/BV1Pg411574f
https://www.bilibili.com/video/BV1864y1h7e7
https://www.bilibili.com/video/BV1Uw411f7my
https://www.bilibili.com/video/BV1XL4y1Y7zz
https://www.bilibili.com/video/BV1AA411w79C
https://www.bilibili.com/video/BV1Ab4y1U75K
https://www.bilibili.com/video/BV1rb4y1m76C
https://www.bilibili.com/video/BV1Sf4y1P7vo
https://www.bilibili.com/video/BV1Jq4y1D77a
https://www.bilibili.com/video/BV1jv411N75Y
https://www.bilibili.com/video/BV1b64y1q7bQ
https://www.bilibili.com/video/BV1Pg411j7M5
https://www.bilibili.com/video/BV1sh411B7jg
https://www.bilibili.com/video/BV1ah411B7Ph
https://www.bilibili.com/video/BV1Fo4y1D7rE
https://www.bilibili.com/video/BV1CU4y1J7Gx
https://www.bilibili.com/video/BV1BU4y1J7Bs
https://www.bilibili.com/video/BV1vM4y157Cm
https://www.bilibili.com/video/BV1844y1C7TC
https://www.bilibili.com/video/BV1Gb4y1z7n9
https://www.bilibili.com/video/BV12M4y1N7EB
https://www.bilibili.com/video/BV1D64y1B7qf
https://www.bilibili.com/video/BV1W64y167sB
https://www.bilibili.com/video/BV1NP4y1t7bi
https://www.bilibili.com/video/BV1ff4y157F3
https://www.bilibili.com/video/BV1rv411E75w
https://www.bilibili.com/video/BV1S64y1z77E
https://www.bilibili.com/video/BV1sy4y1j7Vv
https://www.bilibili.com/video/BV1V64y1x72K
https://www.bilibili.com/video/BV1Zf4y1V7ph
https://www.bilibili.com/video/BV1y44y127zb
https://www.bilibili.com/video/BV1Zy4y1L7MD
https://www.bilibili.com/video/BV1Cw411975e
https://www.bilibili.com/video/BV1Vg411M7Ms
https://www.bilibili.com/video/BV1BL411W7q6
https://www.bilibili.com/video/BV1cg411M7aK
https://www.bilibili.com/video/BV1bL411H7JT
https://www.bilibili.com/video/BV1oV411W7VE
https://www.bilibili.com/video/BV1BX4y1F7CZ
https://www.bilibili.com/video/BV1Yy4y1K7AQ

https://www.bilibili.com/video/BV1yb4y1r7bv
https://www.bilibili.com/video/BV1eK4y1M7zi
https://www.bilibili.com/video/BV1Mo4y1X7ao
https://www.bilibili.com/video/BV1E64y1b7G4
https://www.bilibili.com/video/BV1eo4y1C7qn
https://www.bilibili.com/video/BV11L411p7va
https://www.bilibili.com/video/BV14K4y1g7cB
https://www.bilibili.com/video/BV1Ev411H7rb
https://www.bilibili.com/video/BV19b4y1C7om
https://www.bilibili.com/video/BV13h411h7J7
https://www.bilibili.com/video/BV1564y1b7LB
https://www.bilibili.com/video/BV1HV411x7MJ
https://www.bilibili.com/video/BV1Wg41137v8
https://www.bilibili.com/video/BV1M64y197QP
https://www.bilibili.com/video/BV1XU4y1G78t
https://www.bilibili.com/video/BV1C64y1t77D
https://www.bilibili.com/video/BV1xh411Y7cH
https://www.bilibili.com/video/BV1Jo4y1k7RQ
https://www.bilibili.com/video/BV1654y1G7xG
https://www.bilibili.com/video/BV1Ky4y1g7PX
https://www.bilibili.com/video/BV1vU4y157Kb
https://www.bilibili.com/video/BV1ow411d7wo
https://www.bilibili.com/video/BV1N64y1r77A
https://www.bilibili.com/video/BV1Eq4y177Bf
https://www.bilibili.com/video/BV1yQ4y197EX
https://www.bilibili.com/video/BV1j44y1B7Js
https://www.bilibili.com/video/BV1VK4y197Sw
https://www.bilibili.com/video/BV1j64y1o74D

'''.split('\n')
cleanup = True#False
import subprocess
outdir = '/tf/out' #os.getcwd()#r'D:\tmp\ytd\hedvika'
from inaseg import extract_music, segment, extract_mah_stuff
import os
for media in rs:
    if media == '': continue
    if 'https:' in media: media = ytbdl(media, soundonly = '', aria = 16)#, outdir = outdir
    extract_mah_stuff(media, extract_music(segment(media)), outdir = outdir, rev=False, soundonly = False)    
    print('inaseg completed on', media)
    shazaming(outdir, media, threads = 4)
    stripped_media_names = strip_medianame_out(outdir, media)
    print('preparing to upload', stripped_media_names)
    #b站大小姐只想让我上传10p？？
    #well apparently biliup checks json at current DIR instead of its dir
    os.chdir('/tf/out')
    bilibili_upload(stripped_media_names, os.path.basename(media), source = None, episode_limit=180)
    if cleanup:
        os.remove(media)
        for i in stripped_media_names: os.remove(i)
    print('finished stripping and uploading', media)
    if not cleanup: put_medianame_backin(stripped_media_names, media, shazamed = r'D:\tmp\ytd\convert2music', nonshazamed = r'D:\tmp\ytd\extract')