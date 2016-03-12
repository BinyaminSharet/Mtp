from __future__ import absolute_import
from .mtp_data_types import UInt8, UInt16
from .mtp_proto import ResponseCodes
from .mtp_exception import MtpProtocolException


class MtpPropertyCode(object):
    DPC_Undefined = 0x5000
    DPC_BatteryLevel = 0x5001
    DPC_FunctionalMode = 0x5002
    DPC_ImageSize = 0x5003
    DPC_CompressionSetting = 0x5004
    DPC_WhiteBalance = 0x5005
    DPC_RGBGain = 0x5006
    DPC_FNumber = 0x5007
    DPC_FocalLength = 0x5008
    DPC_FocusDistance = 0x5009
    DPC_FocusMode = 0x500A
    DPC_ExposureMeteringMode = 0x500B
    DPC_FlashMode = 0x500C
    DPC_ExposureTime = 0x500D
    DPC_ExposureProgramMode = 0x500E
    DPC_ExposureIndex = 0x500F
    DPC_ExposureBiasCompensation = 0x5010
    DPC_DateTime = 0x5011
    DPC_CaptureDelay = 0x5012
    DPC_StillCaptureMode = 0x5013
    DPC_Contrast = 0x5014
    DPC_Sharpness = 0x5015
    DPC_DigitalZoom = 0x5016
    DPC_EffectMode = 0x5017
    DPC_BurstNumber = 0x5018
    DPC_BurstInterval = 0x5019
    DPC_TimelapseNumber = 0x501A
    DPC_TimelapseInterval = 0x501B
    DPC_FocusMeteringMode = 0x501C
    DPC_UploadURL = 0x501D
    DPC_Artist = 0x501E
    DPC_CopyrightInfo = 0x501F
    DPC_SupportedStreams = 0x5020
    DPC_EnabledStreams = 0x5021
    DPC_VideoFormat = 0x5022
    DPC_VideoResolution = 0x5023
    DPC_VideoQuality = 0x5024
    DPC_VideoFrameRate = 0x5025
    DPC_VideoContrast = 0x5026
    DPC_VideoBrightness = 0x5027
    DPC_AudioFormat = 0x5028
    DPC_AudioBitrate = 0x5029
    DPC_AudioSamplingRate = 0x502A
    DPC_AudioBitPerSample = 0x502B
    DPC_AudioVolume = 0x502C
    DPC_MTP_SecureTime = 0xD101
    DPC_MTP_DeviceCertificate = 0xD102
    DPC_MTP_RevocationInfo = 0xD103
    DPC_MTP_SynchronizationPartner = 0xD401
    DPC_MTP_DeviceFriendlyName = 0xD402
    DPC_MTP_VolumeLevel = 0xD403
    DPC_MTP_DeviceIcon = 0xD405
    DPC_MTP_SessionInitiatorInfo = 0xD406
    DPC_MTP_PerceivedDeviceType = 0xD407
    DPC_MTP_PlaybackRate = 0xD410
    DPC_MTP_PlaybackObject = 0xD411
    DPC_MTP_PlaybackContainerIndex = 0xD412
    DPC_MTP_PlaybackPosition = 0xD413
    DPC_MTP_PlaysForSureID = 0xD131

    # MTP specific Object Properties
    OPC_StorageID = 0xDC01
    OPC_ObjectFormat = 0xDC02
    OPC_ProtectionStatus = 0xDC03
    OPC_ObjectSize = 0xDC04
    OPC_AssociationType = 0xDC05
    OPC_AssociationDesc = 0xDC06
    OPC_ObjectFileName = 0xDC07
    OPC_DateCreated = 0xDC08
    OPC_DateModified = 0xDC09
    OPC_Keywords = 0xDC0A
    OPC_ParentObject = 0xDC0B
    OPC_AllowedFolderContents = 0xDC0C
    OPC_Hidden = 0xDC0D
    OPC_SystemObject = 0xDC0E
    OPC_PersistantUniqueObjectIdentifier = 0xDC41
    OPC_SyncID = 0xDC42
    OPC_PropertyBag = 0xDC43
    OPC_Name = 0xDC44
    OPC_CreatedBy = 0xDC45
    OPC_Artist = 0xDC46
    OPC_DateAuthored = 0xDC47
    OPC_Description = 0xDC48
    OPC_URLReference = 0xDC49
    OPC_LanguageLocale = 0xDC4A
    OPC_CopyrightInformation = 0xDC4B
    OPC_Source = 0xDC4C
    OPC_OriginLocation = 0xDC4D
    OPC_DateAdded = 0xDC4E
    OPC_NonConsumable = 0xDC4F
    OPC_CorruptOrUnplayable = 0xDC50
    OPC_ProducerSerialNumber = 0xDC51
    OPC_RepresentativeSampleFormat = 0xDC81
    OPC_RepresentativeSampleSize = 0xDC82
    OPC_RepresentativeSampleHeight = 0xDC83
    OPC_RepresentativeSampleWidth = 0xDC84
    OPC_RepresentativeSampleDuration = 0xDC85
    OPC_RepresentativeSampleData = 0xDC86
    OPC_Width = 0xDC87
    OPC_Height = 0xDC88
    OPC_Duration = 0xDC89
    OPC_Rating = 0xDC8A
    OPC_Track = 0xDC8B
    OPC_Genre = 0xDC8C
    OPC_Credits = 0xDC8D
    OPC_Lyrics = 0xDC8E
    OPC_SubscriptionContentID = 0xDC8F
    OPC_ProducedBy = 0xDC90
    OPC_UseCount = 0xDC91
    OPC_SkipCount = 0xDC92
    OPC_LastAccessed = 0xDC93
    OPC_ParentalRating = 0xDC94
    OPC_MetaGenre = 0xDC95
    OPC_Composer = 0xDC96
    OPC_EffectiveRating = 0xDC97
    OPC_Subtitle = 0xDC98
    OPC_OriginalReleaseDate = 0xDC99
    OPC_AlbumName = 0xDC9A
    OPC_AlbumArtist = 0xDC9B
    OPC_Mood = 0xDC9C
    OPC_DRMStatus = 0xDC9D
    OPC_SubDescription = 0xDC9E
    OPC_IsCropped = 0xDCD1
    OPC_IsColorCorrected = 0xDCD2
    OPC_ImageBitDepth = 0xDCD3
    OPC_Fnumber = 0xDCD4
    OPC_ExposureTime = 0xDCD5
    OPC_ExposureIndex = 0xDCD6
    OPC_DisplayName = 0xDCE0
    OPC_BodyText = 0xDCE1
    OPC_Subject = 0xDCE2
    OPC_Priority = 0xDCE3
    OPC_GivenName = 0xDD00
    OPC_MiddleNames = 0xDD01
    OPC_FamilyName = 0xDD02
    OPC_Prefix = 0xDD03
    OPC_Suffix = 0xDD04
    OPC_PhoneticGivenName = 0xDD05
    OPC_PhoneticFamilyName = 0xDD06
    OPC_EmailPrimary = 0xDD07
    OPC_EmailPersonal1 = 0xDD08
    OPC_EmailPersonal2 = 0xDD09
    OPC_EmailBusiness1 = 0xDD0A
    OPC_EmailBusiness2 = 0xDD0B
    OPC_EmailOthers = 0xDD0C
    OPC_PhoneNumberPrimary = 0xDD0D
    OPC_PhoneNumberPersonal = 0xDD0E
    OPC_PhoneNumberPersonal2 = 0xDD0F
    OPC_PhoneNumberBusiness = 0xDD10
    OPC_PhoneNumberBusiness2 = 0xDD11
    OPC_PhoneNumberMobile = 0xDD12
    OPC_PhoneNumberMobile2 = 0xDD13
    OPC_FaxNumberPrimary = 0xDD14
    OPC_FaxNumberPersonal = 0xDD15
    OPC_FaxNumberBusiness = 0xDD16
    OPC_PagerNumber = 0xDD17
    OPC_PhoneNumberOthers = 0xDD18
    OPC_PrimaryWebAddress = 0xDD19
    OPC_PersonalWebAddress = 0xDD1A
    OPC_BusinessWebAddress = 0xDD1B
    OPC_InstantMessengerAddress = 0xDD1C
    OPC_InstantMessengerAddress2 = 0xDD1D
    OPC_InstantMessengerAddress3 = 0xDD1E
    OPC_PostalAddressPersonalFull = 0xDD1F
    OPC_PostalAddressPersonalFullLine1 = 0xDD20
    OPC_PostalAddressPersonalFullLine2 = 0xDD21
    OPC_PostalAddressPersonalFullCity = 0xDD22
    OPC_PostalAddressPersonalFullRegion = 0xDD23
    OPC_PostalAddressPersonalFullPostalCode = 0xDD24
    OPC_PostalAddressPersonalFullCountry = 0xDD25
    OPC_PostalAddressBusinessFull = 0xDD26
    OPC_PostalAddressBusinessLine1 = 0xDD27
    OPC_PostalAddressBusinessLine2 = 0xDD28
    OPC_PostalAddressBusinessCity = 0xDD29
    OPC_PostalAddressBusinessRegion = 0xDD2A
    OPC_PostalAddressBusinessPostalCode = 0xDD2B
    OPC_PostalAddressBusinessCountry = 0xDD2C
    OPC_PostalAddressOtherFull = 0xDD2D
    OPC_PostalAddressOtherLine1 = 0xDD2E
    OPC_PostalAddressOtherLine2 = 0xDD2F
    OPC_PostalAddressOtherCity = 0xDD30
    OPC_PostalAddressOtherRegion = 0xDD31
    OPC_PostalAddressOtherPostalCode = 0xDD32
    OPC_PostalAddressOtherCountry = 0xDD33
    OPC_OrganizationName = 0xDD34
    OPC_PhoneticOrganizationName = 0xDD35
    OPC_Role = 0xDD36
    OPC_Birthdate = 0xDD37
    OPC_MessageTo = 0xDD40
    OPC_MessageCC = 0xDD41
    OPC_MessageBCC = 0xDD42
    OPC_MessageRead = 0xDD43
    OPC_MessageReceivedTime = 0xDD44
    OPC_MessageSender = 0xDD45
    OPC_ActivityBeginTime = 0xDD50
    OPC_ActivityEndTime = 0xDD51
    OPC_ActivityLocation = 0xDD52
    OPC_ActivityRequiredAttendees = 0xDD54
    OPC_ActivityOptionalAttendees = 0xDD55
    OPC_ActivityResources = 0xDD56
    OPC_ActivityAccepted = 0xDD57
    OPC_Owner = 0xDD5D
    OPC_Editor = 0xDD5E
    OPC_Webmaster = 0xDD5F
    OPC_URLSource = 0xDD60
    OPC_URLDestination = 0xDD61
    OPC_TimeBookmark = 0xDD62
    OPC_ObjectBookmark = 0xDD63
    OPC_ByteBookmark = 0xDD64
    OPC_LastBuildDate = 0xDD70
    OPC_TimetoLive = 0xDD71
    OPC_MediaGUID = 0xDD72
    OPC_TotalBitRate = 0xDE91
    OPC_BitRateType = 0xDE92
    OPC_SampleRate = 0xDE93
    OPC_NumberOfChannels = 0xDE94
    OPC_AudioBitDepth = 0xDE95
    OPC_ScanDepth = 0xDE97
    OPC_AudioWAVECodec = 0xDE99
    OPC_AudioBitRate = 0xDE9A
    OPC_VideoFourCCCodec = 0xDE9B
    OPC_VideoBitRate = 0xDE9C
    OPC_FramesPerThousandSeconds = 0xDE9D
    OPC_KeyFrameDistance = 0xDE9E
    OPC_BufferSize = 0xDE9F
    OPC_EncodingQuality = 0xDEA0
    OPC_EncodingProfile = 0xDEA1
    OPC_BuyFlag = 0xD901


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
