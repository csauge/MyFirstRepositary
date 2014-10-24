import argparse # For ArgumentParser
import subprocess # For check_output, call
import sys # For exit, stderr


class UcmVersion:

    def __init__(self, element, previous_version, version):

        self.element = element
        self.previous_version = previous_version
        self.version = version


class UcmActivityDifference:
    """Manage a UCM activity change set"""

    def __init__(self):

        activity = self.argument_parser()
        version_list = self.activity_change_set(activity)
        version_list.reverse() # Get the oldest version first.
        merged_ucm_version_list = []

        for version in version_list:
            ucm_version = self.version_info(version)
            merged = False
            for merged_ucm_version in merged_ucm_version_list:
                if merged_ucm_version.version == ucm_version.previous_version:
                    merged_ucm_version.version = ucm_version.version # Merge two versions together.
                    merged = True
                    break
            if not merged:
                merged_ucm_version_list.append(ucm_version)

        for ucm_version in merged_ucm_version_list:
            print('{}'.format(ucm_version.element))
            print('*** {} -> {}'.format(ucm_version.previous_version, ucm_version.version))
            if '/CHECKEDOUT.' in ucm_version.version: # Case of checkedout, return the element name to make the difference.
                subprocess.call('cleartool diff -graphical -options "-blank_ignore" {0}@@{1} {0}@@{2}'.format(ucm_version.element, ucm_version.previous_version, ucm_version.element), shell=True)
            else:
                subprocess.call('cleartool diff -graphical -options "-blank_ignore" {0}@@{1} {0}'.format(ucm_version.element, ucm_version.previous_version), shell=True)

    def argument_parser(self):
        """Handle arguments of this module"""

        parser = argparse.ArgumentParser(description="Displays graphical UCM activity differences. You must be in a UCM view.")
        parser.add_argument('activity', help="UCM activity.")
        return parser.parse_args().activity

    def activity_change_set(self, activity):

        output = subprocess.check_output('cleartool lsactivity -fmt "%[versions]CQp" {}'.format(activity), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        if '' == output:
            return [] # Empty list for empty changet set.
        return [version.strip('"') for version in output.split(', ')] # Remove the commas and double quotes and create a list of versions.

    def version_info(self, version):

       output = subprocess.check_output('cleartool describe -fmt "%En\t%PVn\t%Vn" {}'.format(version), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
       element, previous_version, version = output.split('\t')
       return UcmVersion(element, previous_version, version)

if __name__ == '__main__':

    try:
        UcmActivityDifference()
    except KeyboardInterrupt:
        print('Error: User aborted.', file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(e.output.decode('ascii'), end='', file=sys.stderr)
        sys.exit(1)
