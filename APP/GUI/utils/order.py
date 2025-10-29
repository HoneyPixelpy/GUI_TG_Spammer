import random

from loguru import logger

from APP.GUI.utils.custom_widgets import ErrorAlert
from APP.GUI.utils.errors import ConfigDataError,AccountDataError,SettingsDataError
from APP.GUI.utils.file_manager import ConfigData, SettingsData




class StartWork:
    
    def check_start_data(
        self,
        config_data: dict
        ) -> dict:
        """
        Проверяем конфигурационные данные
        
        ['channel_data'] -> Определяет способ рассылки, так как их всего два.
        
        mailing_media_file -> сделать разным для каждого окна с получением медюхи
            (Для того чтобы случайно не пустить в ход медюху, которая была добавленна в другом месте)
            
        Проверить нет ли в софте прямых проверок на (None) для того чтобы можно было передавать ("")
        
        ['neuro_mod'] -> для генерации текста через нейронку
        
        """
        # NOTE проверяем данные для ответов
        if not config_data.get('list_accounts'):
            raise ConfigDataError(
            "Cписок с аккаунта по который должны выполняться работа пуст",
            )
        
        config_data['list_accounts'] = list(set(config_data['list_accounts']))

        assert config_data.get('variation_answer') is not None, ConfigDataError(
            "Нет данных о варианте способа ответа"
            )
        if config_data['variation_answer'] == 0:
            assert config_data.get('answer_static_text_content') is not None, ConfigDataError(
                "Нет данных о тексте для ответов"
                )
            assert config_data.get('answer_media_file') is not None, ConfigDataError(
                "Нет данных о медиафайле для ответов"
                )
            config_data['answer_data'] = {
                    "variation": "static",
                    "text_sms": {
                        "text": {
                            "default": config_data['answer_static_text_content'],
                            "lang": config_data['answer_static_lang_content'],
                            },
                        "language_matching": config_data['translate_fio'],
                        "neuro_mod": False
                    },
                    "media": config_data['answer_media_file'] if (
                        config_data['answer_media_file'] != config_data['default_file']
                        ) else None
                }
        elif config_data['variation_answer'] == 1:
            assert config_data.get('prompt_text_content') is not None, ConfigDataError(
                "Нет данных о Промпте"
                )
            config_data['answer_data'] = {
                    "variation": "II",
                    "prompt": config_data['prompt_text_content']
                }
        elif config_data['variation_answer'] == 2:
            config_data['answer_data'] = {
                    "variation": "dynamic"
                }
        elif config_data['variation_answer'] == 3:
            config_data['answer_data'] = {
                    "variation": None
                }
    
        # NOTE проверки
        assert config_data.get('variation_target') is not None, ConfigDataError(
            "Небыл выбран чекбокс с выриантном целей для рассылки"
            )
        assert config_data.get('variation_base') is not None, ConfigDataError(
            "Небыл выбран чекбокс с типом базы"
            )
        assert config_data.get('base_file') is not None, ConfigDataError(
            "Небыл добавлен файл с базой по которой будем работать"
            )
        assert config_data.get('uniq_profile') is not None, ConfigDataError(
            "Нет данных выбора унакализировать аккаунт или нет"
            )
        assert config_data.get('slow_mode') is not None, ConfigDataError(
            "Нет данных выбора слоу мода"
            )
        assert config_data.get('clear_history_base') is not None, ConfigDataError(
            "Нет данных по очистки истории общения для нейронки"
            )
        assert config_data.get('variation_mailing') is not None, ConfigDataError(
            "Нет данных о варианте способа рассылки"
            )

        # NOTE проверяем данные для сообщения которое будем рассылать (данные канала)
        if config_data['variation_mailing'] == 0:
            config_data['channel_data'] = None
            
            assert config_data.get('static_text_content') is not None, ConfigDataError(
                "Небыл введен текст для рассылки от своего лица"
                )
            assert config_data.get('mailing_media_file') is not None, ConfigDataError(
                "Небыл выбран медиафайл для рассылки от своего лица"
                )
            config_data['message_data'] = {
                "text_sms": {
                    "text": {
                        "default": config_data['static_text_content'],
                        "lang": config_data['static_lang_content'],
                        },
                    "language_matching": config_data['translate_fio'],
                    "neuro_mod": False
                    },
                "media": config_data['mailing_media_file'] if (
                    config_data['mailing_media_file'] != config_data['default_file']
                    ) else None
            }
        elif config_data['variation_mailing'] == 1:
            assert config_data.get('channel_title') is not None, ConfigDataError(
                "Небыл введен Загаловок канала"
                )
            assert config_data.get('channel_description') is not None, ConfigDataError(
                "Небыло введено Описание канала"
                )
            assert config_data.get('channel_btn_text') is not None, ConfigDataError(
                "Небыло введено Название Кнопки"
                )
            assert config_data.get('channel_btn_url') is not None, ConfigDataError(
                "Небыл введен URL для Кнопки"
                )
            config_data['channel_data'] = {
                "title": config_data['channel_title'],
                "description": config_data['channel_description'],
                "text": config_data['channel_btn_text'],
                "link": config_data['channel_btn_url'],
            }
            
            assert config_data.get('channel_text_content') is not None, ConfigDataError(
                "Небыл введен текст для рассылки через канал"
                )
            assert config_data.get('mailing_media_file') is not None, ConfigDataError(
                "Небыл выбран медиафайл для рассылки через канал"
                )
            config_data['message_data'] = {
                "text_sms": {
                    "text": {
                        "default": config_data['channel_text_content'],
                        "lang": None,
                        },
                    "language_matching": None,
                    "neuro_mod": False
                    },
                "media": config_data['mailing_media_file'] if (
                    config_data['mailing_media_file'] != config_data['default_file']
                    ) else None
            }

        # NOTE settings
        assert config_data.get('time_dilay') is not None, SettingsDataError(
            "Настроек с задержками нет"
            )

        time_dilay: dict = config_data["time_dilay"]

        try:
            time_dilay["prof_uniq"]["min"]
            time_dilay["prof_uniq"]["max"]
            time_dilay["pars_chat"]["min"]
            time_dilay["pars_chat"]["max"]
            time_dilay["send_msg_user"]["min"]
            time_dilay["send_msg_user"]["max"]
            time_dilay["send_msg_chat"]["min"]
            time_dilay["send_msg_chat"]["max"]
            time_dilay["invite"]["min"]
            time_dilay["invite"]["max"]
            time_dilay["read_history"]["min"]
            time_dilay["read_history"]["max"]
            time_dilay["error_delay_entity"]["min"]
            time_dilay["error_delay_entity"]["max"]
            time_dilay["auto_responder_static"]["min"]
            time_dilay["auto_responder_static"]["max"]
            time_dilay["auto_responder_II"]["min"]
            time_dilay["auto_responder_II"]["max"]
            time_dilay["after_launch"]["min"]
            time_dilay["after_launch"]["max"]
            time_dilay["between_steps"]["min"]
            time_dilay["between_steps"]["max"]
            time_dilay["peerflooderror"]["min"]
            time_dilay["peerflooderror"]["max"]
            time_dilay["work_acc"]["min"]
            time_dilay["work_acc"]["max"]
        except KeyError as ex:
            raise SettingsDataError(
                str(ex)
            )

        assert isinstance(time_dilay["sleep_blocks"], list), SettingsDataError(
            "sleep_blocks не является списком"
        )

        for sleep_block in time_dilay["sleep_blocks"]:
            assert sleep_block.get("start"), SettingsDataError(
                "у sleep_block нет начала"
            )
            assert sleep_block.get("end"), SettingsDataError(
                "у sleep_block нет конца"
            )

        assert isinstance(config_data["pars_users"], dict), SettingsDataError(
            "pars_users не является cловарём" # TODO тут можно проверить на существующие параметры для парсинга
        )
        assert isinstance(config_data["black_list_buttons"], list), SettingsDataError(
            "black_list_buttons не является списком"
        )
        assert isinstance(config_data["url_list_buttons"], list), SettingsDataError(
            "url_list_buttons не является списком"
        )
        
        try:
            config_data["const"]["system_version"]
            config_data["settings_mailing_chats"]["repeats"]
            config_data["settings_mailing_chats"]["wait_msg_chats"]
            config_data["settings_II"]["prompt"]
            config_data["settings_dilay_mailing_to_target"]["user"]
            config_data["settings_dilay_mailing_to_target"]["chat"]
        except KeyError as ex:
            raise SettingsDataError(
                str(ex)
            )

        config_data['id'] = str(random.randint(100000,999999))
        return config_data

    def get_start_data(
        self
        ) -> dict:
        config_data = ConfigData.get_all()
        settings_data = SettingsData.get_all()
        return config_data | settings_data

    def start(
        self
        ) -> dict:
        try:
            logger.debug("Нажали на кнопку")
            start_data = self.check_start_data(
                self.get_start_data()
                )
            del start_data['default_file']
            del start_data['no_doc_file']
            del start_data['yes_doc_file']
            return start_data
        except (ConfigDataError,AccountDataError,SettingsDataError) as ex:
            ErrorAlert().show_message(
                ex.title,
                ex.description
            )
        except Exception as ex:
            logger.exception("Ошибка в работе софта")
            ErrorAlert().show_message(
                "Новая ошибка",
                f"{ex.__class__.__name__}: {ex}"
            )


