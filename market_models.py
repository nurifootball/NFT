from django.db import models
from django.utils import timezone

from core import models as core_models
from nft import models as nft_models
from users import models as users_models
import datetime
# Create your models here.


class SellList(core_models.TimeStampeModel):
    """
        판매 등록한 NFT 정보
    """
    sell_card = models.ForeignKey(nft_models.NFTCard, related_name="sell_card",on_delete=models.CASCADE, null=True,blank=False)
    res_price = models.IntegerField("가격",default=0)
    sel_price = models.IntegerField("판매 가격", default=0)

    seller = models.ForeignKey(users_models.User, related_name="seller", on_delete=models.CASCADE, null=True,blank=False)
    is_selling = models.BooleanField("판매 상태", default=False, null=True,blank=True)


class NFTTransactionHistory(core_models.TimeStampeModel):
    """
        NFT 거래 내역
    """
    buyer = models.ForeignKey(users_models.User, related_name="Buyer", on_delete=models.CASCADE, null=True,blank=False)
    transaction_info = models.ForeignKey(SellList,related_name="transaction_info", on_delete=models.SET_NULL, null=True,blank=False)
    from_address = models.TextField("보낸이",blank=True,default="")
    to_address = models.TextField("받은이", default="")
    tx_hash = models.TextField("tx_hash", default="")
    is_NRFB = models.BooleanField('지갑 or 계정', default=True)
    amount = models.IntegerField("송금 수량", default=0)
    is_status = models.BooleanField("거래 상태", default=False, null=True, blank=True)

    def check_one_day(self):
        if (timezone.now() - self.created) > datetime.timedelta(days=1):
            return True
        return False


class NFTTransactionError(core_models.TimeStampeModel):
    """
        NFT 거래 시 에러 발생 시 기록용
    """
    error_str = models.TextField("에러 내용",default="ERROR")
    error_user = models.ForeignKey(users_models.User,related_name="error_user",on_delete=models.CASCADE, null=True,blank=False)