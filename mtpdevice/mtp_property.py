from __future__ import absolute_import
from .mtp_data_types import UInt8, UInt16, UInt32, UInt64, UInt128, MStr, MEnum
from .mtp_proto import ResponseCodes
from .mtp_exception import MtpProtocolException


class MtpFormFlag(object):
    NONE = 0x00
    Range = 0x01
    Enumeration = 0x02
    DataTime = 0x03
    FixedLengthArr = 0x04
    RegEx = 0x05
    ByteArray = 0x06
    LongString = 0xff


class MtpDevicePropertyCode(object):
    Undefined = 0x5000
    BatteryLevel = 0x5001
    FunctionalMode = 0x5002
    ImageSize = 0x5003
    CompressionSetting = 0x5004
    WhiteBalance = 0x5005
    RGBGain = 0x5006
    FNumber = 0x5007
    FocalLength = 0x5008
    FocusDistance = 0x5009
    FocusMode = 0x500A
    ExposureMeteringMode = 0x500B
    FlashMode = 0x500C
    ExposureTime = 0x500D
    ExposureProgramMode = 0x500E
    ExposureIndex = 0x500F
    ExposureBiasCompensation = 0x5010
    DateTime = 0x5011
    CaptureDelay = 0x5012
    StillCaptureMode = 0x5013
    Contrast = 0x5014
    Sharpness = 0x5015
    DigitalZoom = 0x5016
    EffectMode = 0x5017
    BurstNumber = 0x5018
    BurstInterval = 0x5019
    TimelapseNumber = 0x501A
    TimelapseInterval = 0x501B
    FocusMeteringMode = 0x501C
    UploadURL = 0x501D
    Artist = 0x501E
    CopyrightInfo = 0x501F
    SupportedStreams = 0x5020
    EnabledStreams = 0x5021
    VideoFormat = 0x5022
    VideoResolution = 0x5023
    VideoQuality = 0x5024
    VideoFrameRate = 0x5025
    VideoContrast = 0x5026
    VideoBrightness = 0x5027
    AudioFormat = 0x5028
    AudioBitrate = 0x5029
    AudioSamplingRate = 0x502A
    AudioBitPerSample = 0x502B
    AudioVolume = 0x502C
    MTP_SecureTime = 0xD101
    MTP_DeviceCertificate = 0xD102
    MTP_RevocationInfo = 0xD103
    MTP_SynchronizationPartner = 0xD401
    MTP_DeviceFriendlyName = 0xD402
    MTP_VolumeLevel = 0xD403
    MTP_DeviceIcon = 0xD405
    MTP_SessionInitiatorInfo = 0xD406
    MTP_PerceivedDeviceType = 0xD407
    MTP_PlaybackRate = 0xD410
    MTP_PlaybackObject = 0xD411
    MTP_PlaybackContainerIndex = 0xD412
    MTP_PlaybackPosition = 0xD413
    MTP_PlaysForSureID = 0xD131


class MtpObjectPropertyCode(object):
    # MTP specific Object Properties
    StorageID = 0xDC01
    ObjectFormat = 0xDC02
    ProtectionStatus = 0xDC03
    ObjectSize = 0xDC04
    AssociationType = 0xDC05
    AssociationDesc = 0xDC06
    ObjectFileName = 0xDC07
    DateCreated = 0xDC08
    DateModified = 0xDC09
    Keywords = 0xDC0A
    ParentObject = 0xDC0B
    AllowedFolderContents = 0xDC0C
    Hidden = 0xDC0D
    SystemObject = 0xDC0E
    PersistantUniqueObjectIdentifier = 0xDC41
    SyncID = 0xDC42
    PropertyBag = 0xDC43
    Name = 0xDC44
    CreatedBy = 0xDC45
    Artist = 0xDC46
    DateAuthored = 0xDC47
    Description = 0xDC48
    URLReference = 0xDC49
    LanguageLocale = 0xDC4A
    CopyrightInformation = 0xDC4B
    Source = 0xDC4C
    OriginLocation = 0xDC4D
    DateAdded = 0xDC4E
    NonConsumable = 0xDC4F
    CorruptOrUnplayable = 0xDC50
    ProducerSerialNumber = 0xDC51
    RepresentativeSampleFormat = 0xDC81
    RepresentativeSampleSize = 0xDC82
    RepresentativeSampleHeight = 0xDC83
    RepresentativeSampleWidth = 0xDC84
    RepresentativeSampleDuration = 0xDC85
    RepresentativeSampleData = 0xDC86
    Width = 0xDC87
    Height = 0xDC88
    Duration = 0xDC89
    Rating = 0xDC8A
    Track = 0xDC8B
    Genre = 0xDC8C
    Credits = 0xDC8D
    Lyrics = 0xDC8E
    SubscriptionContentID = 0xDC8F
    ProducedBy = 0xDC90
    UseCount = 0xDC91
    SkipCount = 0xDC92
    LastAccessed = 0xDC93
    ParentalRating = 0xDC94
    MetaGenre = 0xDC95
    Composer = 0xDC96
    EffectiveRating = 0xDC97
    Subtitle = 0xDC98
    OriginalReleaseDate = 0xDC99
    AlbumName = 0xDC9A
    AlbumArtist = 0xDC9B
    Mood = 0xDC9C
    DRMStatus = 0xDC9D
    SubDescription = 0xDC9E
    IsCropped = 0xDCD1
    IsColorCorrected = 0xDCD2
    ImageBitDepth = 0xDCD3
    Fnumber = 0xDCD4
    ExposureTime = 0xDCD5
    ExposureIndex = 0xDCD6
    DisplayName = 0xDCE0
    BodyText = 0xDCE1
    Subject = 0xDCE2
    Priority = 0xDCE3
    GivenName = 0xDD00
    MiddleNames = 0xDD01
    FamilyName = 0xDD02
    Prefix = 0xDD03
    Suffix = 0xDD04
    PhoneticGivenName = 0xDD05
    PhoneticFamilyName = 0xDD06
    EmailPrimary = 0xDD07
    EmailPersonal1 = 0xDD08
    EmailPersonal2 = 0xDD09
    EmailBusiness1 = 0xDD0A
    EmailBusiness2 = 0xDD0B
    EmailOthers = 0xDD0C
    PhoneNumberPrimary = 0xDD0D
    PhoneNumberPersonal = 0xDD0E
    PhoneNumberPersonal2 = 0xDD0F
    PhoneNumberBusiness = 0xDD10
    PhoneNumberBusiness2 = 0xDD11
    PhoneNumberMobile = 0xDD12
    PhoneNumberMobile2 = 0xDD13
    FaxNumberPrimary = 0xDD14
    FaxNumberPersonal = 0xDD15
    FaxNumberBusiness = 0xDD16
    PagerNumber = 0xDD17
    PhoneNumberOthers = 0xDD18
    PrimaryWebAddress = 0xDD19
    PersonalWebAddress = 0xDD1A
    BusinessWebAddress = 0xDD1B
    InstantMessengerAddress = 0xDD1C
    InstantMessengerAddress2 = 0xDD1D
    InstantMessengerAddress3 = 0xDD1E
    PostalAddressPersonalFull = 0xDD1F
    PostalAddressPersonalFullLine1 = 0xDD20
    PostalAddressPersonalFullLine2 = 0xDD21
    PostalAddressPersonalFullCity = 0xDD22
    PostalAddressPersonalFullRegion = 0xDD23
    PostalAddressPersonalFullPostalCode = 0xDD24
    PostalAddressPersonalFullCountry = 0xDD25
    PostalAddressBusinessFull = 0xDD26
    PostalAddressBusinessLine1 = 0xDD27
    PostalAddressBusinessLine2 = 0xDD28
    PostalAddressBusinessCity = 0xDD29
    PostalAddressBusinessRegion = 0xDD2A
    PostalAddressBusinessPostalCode = 0xDD2B
    PostalAddressBusinessCountry = 0xDD2C
    PostalAddressOtherFull = 0xDD2D
    PostalAddressOtherLine1 = 0xDD2E
    PostalAddressOtherLine2 = 0xDD2F
    PostalAddressOtherCity = 0xDD30
    PostalAddressOtherRegion = 0xDD31
    PostalAddressOtherPostalCode = 0xDD32
    PostalAddressOtherCountry = 0xDD33
    OrganizationName = 0xDD34
    PhoneticOrganizationName = 0xDD35
    Role = 0xDD36
    Birthdate = 0xDD37
    MessageTo = 0xDD40
    MessageCC = 0xDD41
    MessageBCC = 0xDD42
    MessageRead = 0xDD43
    MessageReceivedTime = 0xDD44
    MessageSender = 0xDD45
    ActivityBeginTime = 0xDD50
    ActivityEndTime = 0xDD51
    ActivityLocation = 0xDD52
    ActivityRequiredAttendees = 0xDD54
    ActivityOptionalAttendees = 0xDD55
    ActivityResources = 0xDD56
    ActivityAccepted = 0xDD57
    Owner = 0xDD5D
    Editor = 0xDD5E
    Webmaster = 0xDD5F
    URLSource = 0xDD60
    URLDestination = 0xDD61
    TimeBookmark = 0xDD62
    ObjectBookmark = 0xDD63
    ByteBookmark = 0xDD64
    LastBuildDate = 0xDD70
    TimetoLive = 0xDD71
    MediaGUID = 0xDD72
    TotalBitRate = 0xDE91
    BitRateType = 0xDE92
    SampleRate = 0xDE93
    NumberOfChannels = 0xDE94
    AudioBitDepth = 0xDE95
    ScanDepth = 0xDE97
    AudioWAVECodec = 0xDE99
    AudioBitRate = 0xDE9A
    VideoFourCCCodec = 0xDE9B
    VideoBitRate = 0xDE9C
    FramesPerThousandSeconds = 0xDE9D
    KeyFrameDistance = 0xDE9E
    BufferSize = 0xDE9F
    EncodingQuality = 0xDEA0
    EncodingProfile = 0xDEA1
    BuyFlag = 0xD901


class MtpObjectPropertyDesc(object):

    def __init__(self, code, perm, default_value, group_code, form_flag=MtpFormFlag.NONE, form=None):
        self.code = UInt16(code)
        self.dtype = UInt16(default_value.dtype)
        self.perm = UInt8(perm)
        self.default_value = default_value
        self.group_code = UInt32(group_code)
        self.form_flag = UInt8(form_flag)
        self.form = form

    def get_code(self):
        return self.code.value

    def pack(self):
        desc = b''
        desc += self.code.pack()
        desc += self.dtype.pack()
        desc += self.perm.pack()
        desc += self.default_value.pack()
        desc += self.group_code.pack()
        desc += self.form_flag.pack()
        if self.form:
            desc += self.form.pack()
        return desc

    def can_set(self):
        return self.perm.value == 1


class MtpObjectPropertyDescriptions(object):
    StorageID = MtpObjectPropertyDesc(MtpObjectPropertyCode.StorageID, 0, UInt32(0), 0)
    ObjectFormat = MtpObjectPropertyDesc(MtpObjectPropertyCode.ObjectFormat, 0, UInt16(0), 0)
    ProtectionStatus = MtpObjectPropertyDesc(
        MtpObjectPropertyCode.ProtectionStatus, 0, UInt16(0), 0,
        MtpFormFlag.Enumeration, MEnum(UInt16, [0x0000, 0x0001, 0x8002, 0x8003])
    )
    ObjectSize = MtpObjectPropertyDesc(MtpObjectPropertyCode.ObjectSize, 0, UInt64(0), 0)
    AssociationType = MtpObjectPropertyDesc(
        MtpObjectPropertyCode.AssociationType, 0, UInt16(0), 0,
        MtpFormFlag.Enumeration, MEnum(UInt8, [0, 1])
    )
    AssociationDesc = MtpObjectPropertyDesc(MtpObjectPropertyCode.AssociationDesc, 0, UInt32(0), 0)
    ObjectFileName = MtpObjectPropertyDesc(MtpObjectPropertyCode.ObjectFileName, 0, MStr(''), 0)
    DateCreated = MtpObjectPropertyDesc(MtpObjectPropertyCode.DateCreated, 0, MStr(''), 0, MtpFormFlag.DataTime)
    DateModified = MtpObjectPropertyDesc(MtpObjectPropertyCode.DateModified, 0, MStr(''), 0, MtpFormFlag.DataTime)
    Keywords = MtpObjectPropertyDesc(MtpObjectPropertyCode.Keywords, 0, MStr(''), 0)
    ParentObject = MtpObjectPropertyDesc(MtpObjectPropertyCode.ParentObject, 0, UInt32(0), 0)
    PersistantUniqueObjectIdentifier = MtpObjectPropertyDesc(MtpObjectPropertyCode.PersistantUniqueObjectIdentifier, 0, UInt128(0), 0)
    Name = MtpObjectPropertyDesc(MtpObjectPropertyCode.Name, 0, MStr(''), 0)


class MtpObjectProperty(object):

    def __init__(self, desc, value):
        self.desc = desc
        self.value = value

    def can_set(self):
        return self.desc.can_set()

    def reset_value(self):
        self.set_value(self.desc.default_value.pack())

    def set_value(self, new_value):
        if self.can_set():
            self.value.unpack(new_value)
        else:
            raise MtpProtocolException(ResponseCodes.ACCESS_DENIED)

    def get_code(self):
        return self.desc.get_code()

    def pack(self):
        return self.value.pack()


class MtpDeviceProperty(object):

    def __init__(self, code, perm, value, default_value):
        self.code = UInt16(code)
        self.dtype = UInt16(value.dtype)
        self.perm = UInt8(perm)
        self.value = value
        self.default_value = default_value
        self.form_flag = UInt8(0)

    def can_set(self):
        return self.perm.value == 1

    def reset_value(self):
        self.set_value(self.default_value.pack())

    def set_value(self, new_value):
        if self.can_set():
            self.value.unpack(new_value)
        else:
            raise MtpProtocolException(ResponseCodes.ACCESS_DENIED)

    def get_code(self):
        return self.code.value

    def get_desc(self):
        desc = b''
        desc += self.code.pack()
        desc += self.dtype.pack()
        desc += self.perm.pack()
        desc += self.default_value.pack()
        desc += self.value.pack()
        desc += self.form_flag.pack()
        return desc

    def get_value(self):
        return self.value.pack()
