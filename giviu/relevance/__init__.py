from giviu.models import Users, Giftcard
from social.models import Likes
from random import sample
from genderator.detector import Detector, MALE


def get_random_gender_giftcard(gender=None):
    if gender is None:
        giftcards = Giftcard.objects.filter(status=1)
    else:
        giftcards = Giftcard.objects.filter(gender=gender,
                                            status=1)
    if not giftcards:
        return None

    return sample(giftcards, 1)[0]


def get_random_male_giftcard():
    return get_random_gender_giftcard('male')


def get_random_female_giftcard():
    return get_random_gender_giftcard('female')


def get_random_unisex_giftcard():
    male = get_random_male_giftcard()
    female = get_random_female_giftcard()

    uni = filter(lambda x: x is not None, [male, female])
    if not uni:
        return None
    return sample(uni, 1)[0]


def get_random_giftcard_for_name_detected_gender(name):
    d = Detector()

    def gender(name):
        if ' ' in name:
            name = name.split(' ')[0]
        return 'male' if d.getGender(name) == MALE else 'female'

    if not name or name is None:
        return get_random_unisex_giftcard()

    detected_gender = gender(name)
    return get_random_gender_giftcard(detected_gender)


def get_relevant_giftcard_for_friend(friend):
    '''Will return the most relevant giftcard for given friend.
    For now it will consider:
      * Friend likes
      * Friend gender
    '''
    friend_likes = Likes.get_likes_from_friend(friend['fbid'])
    if friend_likes is not None:
        # Friend has liked some giftcard so we will recommend
        # a sample random as a gift.
        if 'giftcard_likes' in friend_likes:
            like = sample(friend_likes['giftcard_likes'], 1)[0]

            return Giftcard.objects.get(id=like)

    gf = get_random_giftcard_for_name_detected_gender(friend['first_name'])
    if not gf:
        return None

    return gf
