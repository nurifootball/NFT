import datetime
import random

from django.utils import timezone
from django.db import models

from core import models as core_models
from users import models as users_models



class NFTLotsInformation(core_models.TimeStampeModel):
    """
        NFT 뽑기 가격 설정 및 기능 제한
    """
    is_open = models.BooleanField("뽑기 기능 제한 여부", default=False)
    price = models.IntegerField("뽑기 가격",default=100)


class NFTName(core_models.TimeStampeModel):
    """
        NFT 사용 가능 이름 목록
    """
    sur_name = models.CharField("성", max_length=8)
    given_name = models.CharField("이름", max_length=20)
    full_name = models.CharField("full_name", max_length=30,unique=True)
    is_used = models.BooleanField("사용여부", default=False)
    is_nft = models.BooleanField("NFT 용인지 여부", default=False)

    class Meta:
        verbose_name_plural = "[카드 설정] 이름"


class NFTRate(core_models.TimeStampeModel):
    """
        발행 될 NFT 등급 정보
    """
    lots_obj = models.ForeignKey(NFTLotsInformation,on_delete=models.CASCADE,null=True,blank=False)
    is_lots = models.BooleanField("뽑기 가능 여부",default=True)
    rate = models.CharField("등급",max_length=20,null=True,blank=False)
    max_count = models.IntegerField("최대 수량",default=1000000)
    now_count = models.IntegerField("현재 수량", default=0)
    lots_late = models.FloatField("뽑기 확률", default=0)

    min_st = models.IntegerField("최소 능력치",default=30)
    max_st = models.IntegerField("최대 능력치",default=40)


class NFTTeam(core_models.TimeStampeModel):
    """
        발행 가능 NFT 팀 목록
    """
    team_type_list = (
        ('공격형','공격형'),
        ('수비형','수비형'),
        ('밸런스','밸런스'),
        ('공격형 밸런스','공격형 밸런스'),
        ('수비형 밸런스','수비형 밸런스'),
    )

    team_name = models.CharField("팀명", max_length=30, null=False, blank=False)
    team_emblem = models.ImageField("팀 엠블럼", upload_to="Team/emblem", null=True,blank=False)
    team_emblem_for_card = models.ImageField("카드용 이미지 필드", upload_to="Team/logo/",null=True,default=None)
    team_type = models.CharField("팀 타입",max_length=20,choices=team_type_list,default="밸런스")

    total_supply = models.IntegerField("팀 카드 발행 수량", default=100000)
    now_supply = models.IntegerField("현재 발행 된 수량",default=0)
    is_can_lots = models.BooleanField("뽑기 가능 여부",default=True)

    def __str__(self):
        return self.team_name


class NFTPosition(core_models.TimeStampeModel):
    """
        NFT 카드 포지션 정보
    """
    
    TYPE = (
        ('GK','GK'),
        ('DEF','DEF'),
        ('MID','MID'),
        ('ATK','ATK'),
    )
    po = models.CharField('포지션', max_length=3)
    r_po = models.CharField("러프 포지션", max_length=15,default="ATK",choices=TYPE)
    total_supply = models.IntegerField("포지션 보유 수량", default=100000)
    now_supply = models.IntegerField("현재 발행 된 수량", default=0)
    is_can_lots = models.BooleanField("뽑기 가능 여부", default=True)


class NFTCardSetInfo(core_models.TimeStampeModel):
    """
        NFT 카드 정보
    """
    
    player_name = models.CharField("플레이어 네임", max_length=100, null=True, blank=True)

    player_image = models.ImageField("NFT image", upload_to="NFT/Player/image/info/%Y/%m/%d",null=True,default=None)
    video = models.FileField("NFT video",null=True,default=None)
    rate = models.ForeignKey(NFTRate,on_delete=models.SET_NULL, null=True,blank=False)
    position = models.ForeignKey(NFTPosition,on_delete=models.SET_NULL ,null=True,blank=False, default=None)
    team = models.ForeignKey(NFTTeam, on_delete=models.CASCADE, null=False, blank=False)
    des = models.TextField("데스크립션", default="")

    st_1 = models.IntegerField("스테이터스 1", default=40)
    st_2 = models.IntegerField("스테이터스 2", default=40)
    st_3 = models.IntegerField("스테이터스 3", default=40)
    st_4 = models.IntegerField("스테이터스 4", default=40)
    st_5 = models.IntegerField("스테이터스 5", default=40)
    st_6 = models.IntegerField("스테이터스 6", default=40)

    def st_ovr(self):
        ovr = int((self.st_1 + self.st_2 + self.st_3 + self.st_4 + self.st_5 + self.st_6) / 6)

        return ovr

    def get_first_name(self):
        return str(self.player_name).split()[1]



class NFTCard(core_models.TimeStampeModel):
    """
        발행 된 NFT 카드 정보
    """
    card_kind_list = (
        ('Basic','Basic'),
        ('NFT','NFT')
    )

    nft_owner = models.ForeignKey(users_models.User,on_delete=models.SET_NULL,null=True, blank=False,default=None)
    nft_owner_address = models.TextField("소유 지갑",default="",blank=True)
    token_title = models.CharField("토큰 타이틀", max_length=100, null=True, blank=True)
    token_id = models.CharField("토큰 아이디", max_length=10, null=True, blank=False, unique=True)

    is_nft = models.BooleanField("NFT or Basic", default=False)

    nft_info = models.OneToOneField(NFTCardSetInfo,on_delete=models.CASCADE,null=True,default=None)

    is_mint = models.BooleanField("발행완료 여부", default=None, null=True)

    is_out = models.BooleanField("NFT 소유권", default=False, null=True)

    is_selling = models.BooleanField("판매 중 여부", default=False,null=True)

    is_burn = models.BooleanField("소각 여부", default=False)

    is_open = models.BooleanField("랜덤박스 오픈 여부", default=True)

    change_owner_history = models.TextField("오너 변경 히스토리", null=True, blank=True)

    image_ipfs_url = models.TextField("이미지 ipfs url", null=True)
    video_ipfs_url = models.TextField("비디오 ipfs url", null=True, default="")
    token_ipfs_json = models.TextField("토큰 정보(ipfs_json)", null=True, blank=True)
    token_ipfs = models.TextField("IPFS_hash", null=True, blank=True)


    class Meta:
        verbose_name_plural = "발행 된 카드"

    def check_nft_can_selling(self):
        if (self.is_nft and self.is_mint) and (self.is_out is False) and (self.is_selling is False):
            return True
        else:
            return False

    def get_pos(self):
        print(self.for_player)
        return True


class NFTLotsHistory(core_models.TimeStampeModel):
    """
        NFT 뽑기 유저 신청 내역
    """
    lots_types =(
        ("Basic","Basic"),
        ("NFT","NFT"),
        ("Distribute","Distribute")
    )
    from_address = models.TextField("보낸 지갑주소(유너)",null=False,blank=True,default="")
    to_address = models.TextField("받은 지갑주소(오너)",null=False,blank=True,default="")
    lots_user = models.ForeignKey(users_models.User,on_delete=models.CASCADE, null=True,blank=False)
    tx_hash = models.TextField("해시값",null=False, blank=True, default="")
    amount = models.IntegerField("사용 금액", null=True,blank=False, default=0)
    lots_type = models.CharField("뽑기 타입",choices=lots_types, null=False,blank=False,default="Basic", max_length=10)
    lots_count = models.IntegerField("뽑기 수량",default=0)
    is_point_pay = models.BooleanField("포인트 결제 여부", default=False)
    is_result = models.BooleanField("정상처리 여부", null=True, default=None)

    def check_one_day(self):
        if (timezone.now() - self.created) > datetime.timedelta(days=1):
            return True
        return False



class BasicNames(core_models.TimeStampeModel):
    """
        베이직 카드용 이름
    """
    sur_name = models.CharField("성",max_length=8, null=True,blank=False)
    given_name = models.CharField("이름", max_length=15, null=True, blank=False)
    is_used = models.BooleanField("이름 사용 여부", default=False,null=True)


class CombinePartName(core_models.TimeStampeModel):
    """
        NFT 카드 발행 용 이름 이미지
    """
    spelling = models.CharField("철자",max_length=1)
    s_image = models.ImageField("철자 이미지", upload_to="card/background/spelling/image")
    type = models.CharField("철자 타입",max_length=10)


class CombinePartRateSet(core_models.TimeStampeModel):
    """
        NFT 카드 발행용 등급 별 이미지
    """

    rate = models.CharField("등급",max_length=20)
    card_line = models.ImageField("카드라인", upload_to="card/background/line")
    card_outer_glow = models.ImageField("카드효과", upload_to="card/background/outer_glow")
    card_pattern = models.ImageField("카드패턴", upload_to="card/background/pattern")
    card_ranking = models.ImageField("카드등급", upload_to="card/background/ranking")
    card_team_logo = models.ImageField("카드 팀 로코", upload_to="card/background/team_logo")
    card_background = models.ImageField("BackGround",upload_to="card/background")



class CombinePartPlayer(core_models.TimeStampeModel):
    """
        NFT 카드 발행용 선수 이미지
    """
    player_number = models.TextField("플레이어 넘바",default="",blank=True)
    player_image = models.ImageField("선수 이미지",upload_to="card/background/player/%Y/%m/%d")
    is_used = models.BooleanField("이미지 사용 여부", default=False, null=True)
    team_name = models.TextField("팀 이름")
    is_resize = models.BooleanField("리사이징 여부", default=False)
    is_for_basic = models.BooleanField("베이직 이미지", default=False)

    def random_player(self):
        count = self.objects.filter(is_used = False)
        return random.sample(count,1)


class TxHistoryModel(core_models.TimeStampeModel):
    """ 히스토리 모델 상속용 """
    from_address = models.TextField("보낸 주소", blank=True, default="")
    to_address = models.TextField('받은 주소', blank=True, default="")
    tx_hash = models.TextField("tx_hash", blank=True, default="")
    is_stats = models.BooleanField("상태", default=None, null=True)

    class Meta:
        # abstract : model은 model이지만 데이터베이스에는 나타나지 않는 model
        abstract = True

    def check_one_day(self):
        if (timezone.now() - self.created) > datetime.timedelta(days=1):
            return True
        return False


class MintHistory(TxHistoryModel):
    """
        NFT 발행 시 Mint 내역
    """
    mint_nft = models.ForeignKey(NFTCard, on_delete=models.SET_NULL,null=True, default=None)


class SendHistory(TxHistoryModel):
    """
        NFT 전송 시 Send 내역
    """
    send_nft = models.ForeignKey(NFTCard, on_delete=models.SET_NULL,null=True, default=None)


class NFTOutHistory(TxHistoryModel):
    """
        NFT 반출 내역
    """
    out_nft = models.ForeignKey(NFTCard, on_delete=models.SET_NULL,null=True, default=None)
    user = models.ForeignKey(users_models.User, on_delete=models.SET_NULL, null=True)

    def nft_card(self):
        return self.out_nft


