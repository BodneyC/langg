import argparse


# Stolen from:
#  https://stackoverflow.com/questions/18668227/argparse-subcommands-with-nested-namespaces
class SeparateNamespaceArgumentParser(argparse.ArgumentParser):
    def parse_args(self, *args, **kw):
        res = argparse.ArgumentParser.parse_args(self, *args, **kw)
        from argparse import _HelpAction, _SubParsersAction
        for _action in self._subparsers._actions:
            if not isinstance(_action, _SubParsersAction):
                continue
            v = _action.choices[res.cmd]
            op_data = {}
            for _opt_actions in v._optionals._actions:
                if isinstance(_opt_actions, _HelpAction):
                    continue
                n = _opt_actions.dest
                if hasattr(res, n):  # pop the argument
                    op_data[n] = getattr(res, n)
                    delattr(res, n)
            res.op_data = op_data
        return res


# Stolen from: https://gist.github.com/sampsyo/471779
class AliasedSubParsersAction(argparse._SubParsersAction):

    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ','.join(aliases)
            sup = super(AliasedSubParsersAction._AliasedPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help)

    def add_parser(self, name, **kwargs):
        if 'aliases' in kwargs:
            aliases = kwargs['aliases']
            del kwargs['aliases']
        else:
            aliases = []

        parser = super(
            AliasedSubParsersAction, self
        ).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser
        # Make the help text reflect them, first removing old help entry.
        if 'help' in kwargs:
            help = kwargs.pop('help')
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser
