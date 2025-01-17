import unittest
import numpy as np
import requests

from oneibl.one import ONE


class TestSearch(unittest.TestCase):

    def setUp(self):
        # Init connection to the database
        one = ONE(base_url='https://test.alyx.internationalbrainlab.org', username='test_user',
                  password='TapetesBloc18')
        self.One = one

    def test_search_simple(self):
        one = self.One
        # Test users
        usr = ['olivier', 'nbonacchi']
        sl, sd = one.search(users=usr, details=True)
        self.assertTrue(isinstance(sl, list) and isinstance(sd, list))
        self.assertTrue(all([set(usr).issubset(set(u)) for u in [s['users'] for s in sd]]))
        # when the user is a string instead of a list
        sl1, sd1 = one.search(users=['olivier'], details=True)
        sl2, sd2 = one.search(users='olivier', details=True)
        self.assertTrue(sl1 == sl2 and sd1 == sd2)
        ses = one.search(users='olivier', number=6)
        self.assertTrue(not ses)
        # test for the dataset type
        dtyp = ['spikes.times', 'titi.tata']
        sl, sd = one.search(dataset_types=dtyp, details=True)
        self.assertTrue(len(sl) == 0)
        dtyp = ['channels.site']
        sl, sd = one.search(dataset_types=dtyp, details=True)
        self.assertTrue(len(sl) == 2)
        dtyp = ['spikes.times', 'channels.site']
        sl, sd = one.search(dataset_types=dtyp, details=True)
        self.assertTrue(len(sl) == 1)
        # test empty return for non-existent user
        self.assertTrue(len(one.search(users='asdfa')) == 0)
        # test search with the lab keyword
        self.assertTrue(len(one.search(lab='zadorlab')) == 1)


class TestList(unittest.TestCase):

    def setUp(self):
        # Init connection to the database
        one = ONE(base_url='https://test.alyx.internationalbrainlab.org', username='test_user',
                  password='TapetesBloc18')
        eids = ['cf264653-2deb-44cb-aa84-89b82507028a', '4e0b3320-47b7-416e-b842-c34dc9004cf8']
        self.eid = eids[0]
        self.eid2 = eids[1]
        self.One = one

    def test_list(self):
        one = self.One
        # tests with a single input and a list input
        EIDs = [self.eid,
                [self.eid, self.eid2]]
        for eid in EIDs:
            dt = one.list(eid)  # returns dataset-type
            dt = one.list(eid, details=True)
            dt = one.list(eid, keyword='dataset-type')  # returns list
            dt = one.list(eid, keyword='dataset-type', details=True)  # returns SessionDataInfo
            for key in ('subject', 'users', 'lab', 'type', 'start_time', 'end_time'):
                dt = one.list(eid, keyword=key)  # returns dataset-type
                print(key, ': ', dt)
            ses = one.list(eid, keyword='all')
            usr, ses = one.list(eid, keyword='users', details=True)

    def test_list_error(self):
        one = self.One
        a = 0
        eid = self.eid
        try:
            one.list(eid, keyword='tutu')  # throws an error
        except KeyError:
            a = 1
            pass
        self.assertTrue(a == 1)

    def test_help(self):
        one = self.One
        dtypes = one.list(None, keyword='dataset-types')
        one.help(dtypes[0])
        one.help([])

    def test_list_allkeys(self):
        one = self.One
        for k in one.keywords():
            rep = one.list(keyword=k)
            self.assertTrue(len(rep) > 1)


class TestLoad(unittest.TestCase):

    def setUp(self):
        # Init connection to the database
        one = ONE(base_url='https://test.alyx.internationalbrainlab.org', username='test_user',
                  password='TapetesBloc18')
        eids = ['cf264653-2deb-44cb-aa84-89b82507028a', '4e0b3320-47b7-416e-b842-c34dc9004cf8']
        self.eid = eids[0]
        self.eid2 = eids[1]
        self.One = one

    def test_load_multiple_sessions(self):
        # init stuff to run from cli
        one = self.One
        eids = [self.eid, self.eid2]

        # 2 sessions, data exists on both, dclass output
        out = one.load(eids, dataset_types='channels.site', dclass_output=True)
        self.assertTrue(len(out.data) == 2)
        self.assertTrue(all([len(o) == 748 for o in out.data]))
        # same with a list output
        out = one.load(eids, dataset_types='channels.site')
        # we have 2 sessions, thus 2 elements in the list and they're all 748 elements arrays
        self.assertTrue(len(out) == 2)
        self.assertTrue(all([len(o) == 748 for o in out]))

        # here the dataset type only exists for the first session
        out = one.load(eids, dataset_types='licks.times')
        self.assertTrue(len(out) == 2)
        self.assertTrue(len(out[0]) == 5126 and out[1] is None)
        # test the order of output
        out = one.load([eids[-1], eids[0]], dataset_types='licks.times')
        self.assertTrue(len(out) == 2)
        self.assertTrue(len(out[1]) == 5126 and out[0] is None)
        # same with dataclass output
        out = one.load(eids, dataset_types='licks.times', dclass_output=True)
        self.assertTrue(len(out.data) == 2)
        self.assertTrue(len(out.data[0]) == 5126 and out.data[1] is None)
        # now with reversed order and dataclass output
        out = one.load([eids[-1], eids[0]], dataset_types='licks.times', dclass_output=True)
        self.assertTrue(len(out.data) == 2)
        self.assertTrue(len(out.data[1]) == 5126 and out.data[0] is None)

    def test_load(self):
        # Test with 3 actual datasets predefined
        one = self.One
        dataset_types = ['clusters.peakChannel', 'clusters._phy_annotation', 'clusters.probes']
        eid = ('https://test.alyx.internationalbrainlab.org/'
               'sessions/' + self.eid)
        t, cr, cl = one.load(eid, dataset_types=dataset_types)
        d = one.load(eid, dataset_types=dataset_types, dclass_output=True)
        ind = int(np.where(np.array(d.dataset_type) == 'clusters.peakChannel')[0])
        self.assertTrue(np.all(d.data[ind] == t))
        # Now load with another dset inbetween that doesn't exist
        t_, cr_, cl_ = one.load(eid, dataset_types=['clusters.peakChannel', 'turlu',
                                                    'clusters.probes'])
        self.assertTrue(np.all(t == t_))
        self.assertTrue(np.all(cl == cl_))
        self.assertTrue(cr_ is None)
        # Now try in offline mode where the file already exists
        t_ = one.load(eid, dataset_types=['clusters.peakChannel'], offline=True)
        self.assertTrue(np.all(t == t_))

    def test_load_empty(self):
        # Test with a session that doesn't have any dataset on the Flat Iron
        one = self.One
        eid = self.eid
        dataset_types = ['wheel.velocity', 'wheel.timestamps']
        a, b = one.load(eid, dataset_types=dataset_types)
        self.assertTrue(a is None and b is None)

    def test_load_from_uuid(self):
        # Test the query with only the UUID string and not the full URL (no data here)
        one = self.One
        eid = self.eid
        dataset_types = ['wheel.velocity', 'wheel.timestamps']
        aa = one.load(eid, dataset_types=dataset_types)
        self.assertTrue(len(aa) == 2)

    def test_load_all_data_available(self):
        # Test without a dataset list should download everything and output a dictionary
        one = self.One
        eid = self.eid2
        a = one.load(eid)
        self.assertTrue(len(a.data) == 5)

    def test_load_fileformats(self):
        # npy already works for other tests around, tsv and csv implemented so far
        one = self.One
        eid = self.eid
        one.load(eid, dataset_types=['probes.description'])

    def test_session_does_not_exist(self):
        eid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        self.assertRaises(requests.HTTPError, self.One.load, eid)

    def test_load_offline(self):
        a = self.One.load(self.eid, dataset_types='_ibl_lickPiezo.raw.npy', offline=True)
        self.assertTrue(a == [None])


class TestMisc(unittest.TestCase):

    def test_validate_date_range(self):
        from oneibl.one import _validate_date_range
        # test with list of strings
        expval = ['2018-11-04', '2018-11-04']
        val = ['2018-11-04',
               ['2018-11-04'],
               ('2018-11-04'),
               ['2018-11-04', '2018-11-04'],
               ]
        for v in val:
            self.assertEqual(_validate_date_range(v), expval)
        val = ('2018-11-04', '2018-11-04')
        self.assertEqual(_validate_date_range(val), val)


if __name__ == '__main__':
    unittest.main(exit=False)
