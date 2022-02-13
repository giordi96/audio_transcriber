from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5 import uic, QtCore
import socket

from transcriber import Transcriber
from path_manager import get_resource_path


class TranscriberGui(QWidget):
    """
    Graphical user interface for FGI transcriber.
    """

    GF_MSG = "Got transcription file! Press to save it!"
    """
    Got file message, displayed in label when transcription is obtained.
    """

    SF_MSG = "File saved"
    """
    Save file message, displayed in label when transcription is to be saved.
    """

    LANGUAGE = {"Afrikaans": "af",
                "Basque": "eu",
                "Bulgarian": "bg",
                "Catalan": "ca",
                "Arabic (Egypt)": "ar-EG",
                "Arabic(Jordan)": "ar-JO",
                "Arabic(Kuwait)": "ar-KW",
                "Arabic (Lebanon)": "ar-LB",
                "Arabic(Qatar)": "ar-QA",
                "Arabic (UAE)": "ar-AE",
                "Arabic (Morocco)": "ar-MA",
                "Arabic (Iraq)": "ar-IQ",
                "Arabic (Algeria)": "ar-DZ",
                "Arabic (Bahrain)": "ar-BH",
                "Arabic (Lybia)": "ar-LY",
                "Arabic (Oman)": "ar-OM",
                "Arabic (Saudi Arabia)": "ar-SA",
                "Arabic (Tunisia)": "ar-TN",
                "Arabic (Yemen)": "ar-YE",
                "Czech": "cs",
                "Dutch": "nl-NL",
                "English (Australia)": "en-AU",
                "English (Canada)": "en-CA",
                "English (India)": "en-IN",
                "English (New Zealand)": "en-NZ",
                "English (South Africa)": "en-ZA",
                "English (UK)": "en-GB",
                "English (US)": "en-US",
                "Finnish": "fi",
                "French": "fr-FR",
                "Galician": "gl",
                "German": "de-DE",
                "Hebrew": "he",
                "Hungarian": "hu",
                "Icelandic": "is",
                "Italian": "it-IT",
                "Indonesian": "id",
                "Japanese": "ja",
                "Korean": "ko",
                "Latin": "la",
                "Mandarin Chinese": "zh-CN",
                "Traditional Taiwan": "zh-TW",
                "Simplified China": "zh-CN?",
                "Simplified Hong Kong": "zh-HK",
                "Yue Chinese (Traditional Hong Kong)": "zh-yue",
                "Malaysian": "ms-MY",
                "Norwegian": "no-NO",
                "Polish": "pl",
                "Pig Latin": "xx-piglatin",
                "Portuguese": "pt-PT",
                "Portuguese (Brasil)": "pt-BR",
                "Romanian": "ro-RO",
                "Russian": "ru",
                "Serbian": "sr-SP",
                "Slovak": "sk",
                "Spanish (Argentina)": "es-AR",
                "Spanish (Bolivia)": "es-BO",
                "Spanish (Chile)": "es-CL",
                "Spanish (Colombia)": "es-CO",
                "Spanish(Costa Rica)": "es-CR",
                "Spanish(Dominican Republic)": "es-DO",
                "Spanish(Ecuador)": "es-EC",
                "Spanish (El Salvador)": "es-SV",
                "Spanish (Guatemala)": "es-GT",
                "Spanish (Honduras)": "es-HN",
                "Spanish (Mexico)": "es-MX",
                "Spanish (Nicaragua)": "es-NI",
                "Spanish(Panama)": "es-PA",
                "Spanish (Paraguay)": "es-PY",
                "Spanish (Peru)": "es-PE",
                "Spanish (Puerto Rico)": "es-PR",
                "Spanish (Spain)": "es-ES",
                "Spanish (US)": "es-US",
                "Spanish (Uruguay)": "es-UY",
                "Spanish (Venezuela)": "es-VE",
                "Swedish": "sv-SE",
                "Turkish": "tr",
                "Zulu": "zu"
                }
    """
    Available languages to base transcription on.
    """

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(str(get_resource_path(r"gui/transcriber_gui.ui")), self)

        self.transcription = None

        # set combo box
        self._set_language_cb()

        # set reference images
        self.ICON = QIcon(str(get_resource_path(r"res/logo.png")))
        self.TICK_IMG = QPixmap(str(get_resource_path(r"res/tick.png")))
        self.CROSS_IMG = QPixmap(str(get_resource_path(r"res/cross.png")))

        # hide images at startup
        self.setWindowIcon(self.ICON)
        self.got_file_image.hide()
        self.saved_image.hide()

        # assign handlers to button clicks
        self.start_button.clicked.connect(self.start_new_transcription)
        self.save_button.clicked.connect(self.save_file)
        self.see_result_button.clicked.connect(self.see_result)

    def start_new_transcription(self) -> None:
        """
        Executes a new file transcription.
        """
        # if file has been transcribed but not saved, launches the popup
        if (self._is_transcr_present() and not self._is_transcr_saved()):
            clicked_button = self.show_save_popup()
            if clicked_button == QMessageBox.Cancel:
                return

        # if internet is not available, does not start the transcription
        if not self._is_internet_on():
            self.show_internet_absent_popup()
            return

        # set labels, images and progress bars
        self.transcription = None
        self._set_got_file_labels(False)
        self._set_tsb_bar(False)
        self._update_init_bar(0)

        # get mp4 or mp3 file path
        file_path = QFileDialog.getOpenFileName(self,
                                                'Open file',
                                                ".",
                                                "MP3 (*.mp3);;MP4 (*.mp4)")[0]

        if file_path:
            self._transcribe(file_path=file_path)
        else:
            # if no file has been chosen, start button is enabled again
            self.start_button.setEnabled(True)
            self.language_cb.setEnabled(True)

    def save_file(self):
        """
        Saves the current transcription into a file.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Save file",
                                                   "",
                                                   "All Files (*);;Text Files (*.txt)",
                                                   options=options)
        if file_name:
            if not file_name.endswith(".txt"):
                file_name = "".join((file_name, ".txt"))
            with open(file_name, "w") as file:
                file.write(self.transcription)
            self._set_saved_image(True, self.TICK_IMG)

    def see_result(self) -> int:
        """
        Displays a popup showing the got transcription text.

        Returns
        -------
        int
            Clicked popup button.
        """
        msg = QMessageBox()
        msg.setWindowTitle("Transcripted text")
        msg.setText(self.transcription)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        try:
            clicked_button = msg.exec_()
        except:
            clicked_button = None

        return clicked_button

    def show_save_popup(self) -> int:
        """
        Displays the popup reminding to save the transcription file.

        Returns
        -------
        int
            Clicked popup button.
        """
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Warning, transcribed file has not been saved!")
        msg.setInformativeText("By continuing, the file will be lost. Would you "
                               "like to save it before continuing?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(
            QMessageBox.Save | QMessageBox.Ignore | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Save)

        try:
            clicked_button = msg.exec_()
        except:
            clicked_button = None

        if clicked_button == QMessageBox.Save:
            self.save_file()

        return clicked_button

    def show_internet_absent_popup(self) -> int:
        msg = QMessageBox()
        msg.setWindowTitle("Internet connection absent")
        msg.setText("Warning: Internet connection is not available")
        msg.setInformativeText("The transcription method is based on internet "
                               "connection so can't start without it.")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        try:
            clicked_button = msg.exec_()
        except:
            clicked_button = None

        return clicked_button

    def _transcribe(self, file_path: str) -> None:
        """
        File transcription routine.

        Parameters
        ----------
        file_path : str
            Path to the file to transcribe.
        """
        # sets initialization progress bar
        self._set_init_bar(True)

        # assigns a Transcriber to a thread
        self.thread = QtCore.QThread()
        self.transcriber = Transcriber()
        self.transcriber.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.transcriber.run(
            file_path=file_path,
            language=self.LANGUAGE[self.language_cb.currentText()]))

        # Transcriber progress bars update handlers
        self.transcriber.init_progress.connect(self._update_init_bar)
        self.transcriber.tsb_progress.connect(self._update_tsb_bar)

        # Transcriber.finished handlers
        self.transcriber.finished.connect(self._import_transcription)
        self.transcriber.finished.connect(
            lambda: self._set_got_file_labels(True))
        self.transcriber.finished.connect(self.thread.quit)
        self.transcriber.finished.connect(self.transcriber.deleteLater)

        # thread.finished handlers
        self.thread.finished.connect(self.thread.deleteLater)

        # starts then transcription
        self.thread.start()
        self.start_button.setEnabled(False)
        self.language_cb.setEnabled(False)

    def _set_init_bar(self, enable: bool) -> None:
        """
        Sets the file initialization progress bar.

        Parameters
        ----------
        enable : bool
            If True, bar is enabled, else disabled.
        """
        MSG = "File initialization"
        if enable:
            self.init_label.setText(MSG)
            self.init_bar.setEnabled(True)
            self.init_bar.setTextVisible(True)
        else:
            self.init_label.setText("")
            self.init_bar.setEnabled(False)
            self._update_init_bar(0)

    def _update_init_bar(self, progress: float) -> None:
        """
        Updates the value of the file initialization progress bar.

        If 100% is set, the file transcription progress bar is enabled.

        Parameters
        ----------
        progress : float
            Percentage value to set.
        """
        self.init_bar.setValue(progress)
        if progress == 100:
            self._set_tsb_bar(True)

    def _set_tsb_bar(self, enable: bool):
        """
        Sets the file transcription progress bar.

        Parameters
        ----------
        enable : bool
            If True, bar is enabled, else disabled.
        """
        MSG = "File transcription"
        if enable:
            self.tsb_label.setText(MSG)
            self.tsb_bar.setEnabled(True)
            self.tsb_bar.setTextVisible(True)
        else:
            self.tsb_label.setText("")
            self.tsb_bar.setEnabled(False)
            self._update_tsb_bar(0)

    def _update_tsb_bar(self, progress: float) -> None:
        """
        Updates the value of the file transcription progress bar.

        If 100% is set, the start button is enabled.

        Parameters
        ----------
        progress : float
            Percentage value to set.
        """
        self.tsb_bar.setValue(progress)
        self.start_button.setEnabled(progress == 100)
        self.language_cb.setEnabled(progress == 100)

    def _set_got_file_labels(self, enable: bool) -> None:
        """
        Sets the labels and the images related to the end of transcription process.

        Parameters
        ----------
        enable : bool
            If True, labels and images are displayed.
        """
        if enable:
            self.got_file_label.setText(self.GF_MSG)
            self._set_got_file_image(True, self.TICK_IMG)

            self.saved_label.setText(self.SF_MSG)
            self._set_saved_image(True, self.CROSS_IMG)

            self.save_button.setEnabled(True)
            self.see_result_button.setEnabled(True)
        else:
            self.got_file_label.setText("")
            self._set_got_file_image(False)

            self.saved_label.setText("")
            self._set_saved_image(False)

            self.save_button.setEnabled(False)
            self.see_result_button.setEnabled(False)

    def _set_got_file_image(self, enable: bool, pixmap: QPixmap = None) -> None:
        """
        Sets got_file_image.

        Parameters
        ----------
        enable : bool
            If False image is hidden, if True and pixmap is not None
            the pixmap is set as image and it is shown.
        pixmap : QPixmap
            Pixmap to map on the image, by default None
        """
        if enable and pixmap:
            self.got_file_image.setPixmap(pixmap)
            self.got_file_image.show()
        elif not enable:
            self.got_file_image.hide()

    def _set_saved_image(self, enable: bool, pixmap: QPixmap = None) -> None:
        """
        Sets saved_image.

        Parameters
        ----------
        enable : bool
            If False image is hidden, if True and pixmap is not None
            the pixmap is set as image and it is shown.
        pixmap : QPixmap
            Pixmap to map on the image, by default None
        """
        if enable and pixmap:
            self.saved_image.setPixmap(pixmap)
            self.saved_image.show()
        elif not enable:
            self.saved_image.hide()

    def _import_transcription(self):
        """
        Imports the current transcription from the Transcriber instance.
        """
        self.transcription = self.transcriber.transcription

    def _set_language_cb(self) -> None:
        """
        Sets the combo box to select the audio language.
        """
        self.language_cb.clear()  # clears the combo box
        self.language_cb.addItems(self.LANGUAGE.keys())  # sets the options
        self.language_cb.setCurrentText("Italian")  # sets the default value

    def _is_internet_on(self) -> bool:
        """
        Checks if internet connection is available.

        Returns
        -------
        bool
            True if internet connection is available False otherwise. 
        """

        try:
            socket.create_connection(('Google.com', 80))
            result = True
        except OSError:
            result = False
        return result

    def _is_transcr_present(self) -> bool:
        """
        Checks if a transcription is available.

        Returns
        -------
        bool
            True if a transcription is available.
        """
        return not self.saved_image.isHidden()

    def _is_transcr_saved(self) -> bool:
        """
        Checks if current transcription has been saved.

        Returns
        -------
        bool
            True if current transcription has been saved
        """
        return self.saved_image.pixmap().toImage() == self.TICK_IMG.toImage()
