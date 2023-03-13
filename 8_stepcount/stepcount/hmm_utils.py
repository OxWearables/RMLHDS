import numpy as np


class HMMSmoother():
    def __init__(
        self,
        n_components=None,
        train_test_split=False,
        ste="st",
        startprob=None,
        emissionprob=None,
        transmat=None,
        n_iter=100,
        n_trials=100,
        random_state=123,
        stratify_groups=True,
    ) -> None:
        self.train_test_split = train_test_split
        self.ste = ste
        self.startprob = startprob
        self.emissionprob = emissionprob
        self.transmat = transmat
        self.n_iter = n_iter
        self.n_trials = n_trials
        self.random_state = random_state
        self.stratify_groups = stratify_groups

    def fit(self, Y_pred, Y_true, groups=None):
        self.labels = np.unique(Y_true)
        if self.startprob is None:
            self.startprob = compute_prior(Y_true, self.labels)
        if self.emissionprob is None:
            self.emissionprob = compute_emission(Y_pred, Y_true, self.labels)
        if self.transmat is None:
            self.transmat = compute_transition(Y_true, self.labels, groups)
        return self

    def predict(self, Y, groups=None):
        return self.viterbi(Y, groups)

    def viterbi(self, Y, groups=None):
        params = {
            'prior': self.startprob,
            'emission': self.emissionprob,
            'transition': self.transmat,
            'labels': self.labels,
        }
        if groups is None:
            Y_vit = viterbi(Y, params)
        else:
            Y_vit = np.concatenate([
                viterbi(Y[groups == g], params)
                for g in ordered_unique(groups)
            ])
        return Y_vit


def compute_transition(Y, labels=None, groups=None):
    """ Compute transition matrix from sequence """

    if labels is None:
        labels = np.unique(Y)

    def _compute_transition(Y):
        transition = np.vstack([
            np.sum(Y[1:][(Y == label)[:-1]].reshape(-1, 1) == labels, axis=0)
            for label in labels
        ])
        return transition

    if groups is None:
        transition = _compute_transition(Y)
    else:
        transition = sum((
            _compute_transition(Y[groups == g])
            for g in ordered_unique(groups)
        ))

    transition = transition / np.sum(transition, axis=1).reshape(-1, 1)

    return transition


def compute_emission(Y_pred, Y_true, labels=None):
    """ Compute emission matrix from predicted and true sequences """

    if labels is None:
        labels = np.unique(Y_true)

    if Y_pred.ndim == 1:
        Y_pred = np.hstack([
            (Y_pred == label).astype('float')[:, None]
            for label in labels
        ])

    emission = np.vstack(
        [np.mean(Y_pred[Y_true == label], axis=0) for label in labels]
    )

    return emission


def compute_prior(Y_true, labels=None, uniform=True):
    """ Compute prior probabilities from sequence """

    if labels is None:
        labels = np.unique(Y_true)

    if uniform:
        # all labels with equal probability
        prior = np.ones(len(labels)) / len(labels)

    else:
        # label probability equals observed rate
        prior = np.mean(Y_true.reshape(-1, 1) == labels, axis=0)

    return prior


def viterbi(Y, hmm_params):
    ''' https://en.wikipedia.org/wiki/Viterbi_algorithm '''

    def log(x):
        SMALL_NUMBER = 1e-16
        return np.log(x + SMALL_NUMBER)

    prior = hmm_params['prior']
    emission = hmm_params['emission']
    transition = hmm_params['transition']
    labels = hmm_params['labels']

    nobs = len(Y)
    nlabels = len(labels)

    Y = np.where(Y.reshape(-1, 1) == labels)[1]  # to numeric

    probs = np.zeros((nobs, nlabels))
    probs[0, :] = log(prior) + log(emission[:, Y[0]])
    for j in range(1, nobs):
        for i in range(nlabels):
            probs[j, i] = np.max(
                log(emission[i, Y[j]]) +
                log(transition[:, i]) +
                probs[j - 1, :])  # probs already in log scale
    viterbi_path = np.zeros_like(Y)
    viterbi_path[-1] = np.argmax(probs[-1, :])
    for j in reversed(range(nobs - 1)):
        viterbi_path[j] = np.argmax(
            log(transition[:, viterbi_path[j + 1]]) +
            probs[j, :])  # probs already in log scale

    viterbi_path = labels[viterbi_path]  # to labels

    return viterbi_path


def ordered_unique(x):
    """ np.unique without sorting """
    return x[np.sort(np.unique(x, return_index=True)[1])]
